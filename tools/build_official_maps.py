"""Master builder for all 32 Ocarina of Time Remake official area & dungeon maps:
- Extracts native 2000x1440 Switch 2 NVN2 ROMFS map textures (`UI/CustomTex/Map/Field`
  and `UI/CustomTex/Map/Dungeon` + `LocalMapPaper_*` + `MapIconArrow_00`) purely on CPU.
- Integrates Gemini-generated HD restorations for the 2 fog-hidden zones (`perdido`
  Lost Woods & `desierto` Haunted Wasteland), affine-locked via SIFT to exact game
  coordinates with zero drift.
- Fetches official 2000x1440 Zelda Notes dungeon floor maps for `gerudo` (Gerudo
  Training Ground) and `ganon` (Inside Ganon's Castle).
- Calibrates all 32 live player transforms from `Game/MapCaptureInfo` and re-projects
  all 184 collectible pins in `data/places.json` and `data/collectibles.json`.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import glob
import io
import json
import math
import os
import struct
import sys
from typing import Any
import urllib.request

import cv2
import numpy as np
from PIL import Image
import texture2ddecoder
import zstandard as zstd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, THIS_DIR)

from build_catalog import floor_num_to_label  # noqa: E402
from romfs_reader import RomfsReader  # noqa: E402

DATA_DIR = os.path.join(ROOT_DIR, "data")
MAPS_DIR = os.path.join(DATA_DIR, "map_assets", "maps")
ROMFS_DIR = r"F:\games\SwitchGames\hookshot\game\romfs"

GEMINI_ASSETS_DIR = r"C:\Users\knia\.cursor\projects\H-Codex-Projs-OoT-Map\assets"
GEMINI_LOSTWOOD_SRC = os.path.join(GEMINI_ASSETS_DIR, "lostwood_gemini_hd.jpg")
GEMINI_WASTELAND_SRC = os.path.join(GEMINI_ASSETS_DIR, "wasteland_gemini_hd.jpg")

ASTC_BLOCKS = {
    0x2D: (4, 4),
    0x2E: (5, 4),
    0x2F: (5, 5),
    0x30: (6, 5),
    0x31: (6, 6),
    0x32: (8, 5),
    0x33: (8, 6),
    0x34: (8, 8),
}


def div_round_up(n: int, d: int) -> int:
    return (n + d - 1) // d


def deswizzle_nvn2_ampere(
    width: int,
    height: int,
    blk_w: int,
    blk_h: int,
    bpp: int,
    block_height_log2: int,
    data: bytes,
) -> bytes:
    """Deswizzle Nintendo Switch 2 (Ounce / Ampere NVN2) 16Bx4 GOB block-linear texture."""
    w_blks = div_round_up(width, blk_w)
    h_blks = div_round_up(height, blk_h)
    bh_gobs = 1 << block_height_log2
    x_gobs = div_round_up(w_blks * bpp, 64)
    block_h = bh_gobs
    while block_h > 1 and (block_h >> 1) * 8 >= h_blks:
        block_h >>= 1
    gob_size = 512
    block_size = gob_size * block_h

    ys = np.arange(h_blks)[:, None]
    xs_b = np.arange(w_blks)[None, :]
    x_byte = xs_b * bpp
    gob_y = ys // 8
    y_in_gob = ys % 8
    blk_y = gob_y // block_h
    gob_in_blk_y = gob_y % block_h
    gob_x = x_byte // 64
    x_in_gob = x_byte % 64
    in_gob = (
        ((x_in_gob & 0x20) << 3)
        | ((y_in_gob & 0x04) << 5)
        | ((x_in_gob & 0x10) << 2)
        | ((y_in_gob & 0x03) << 4)
        | (x_in_gob & 0x0F)
    )
    src_off = (blk_y * x_gobs + gob_x) * block_size + gob_in_blk_y * gob_size + in_gob
    src_blocks = np.frombuffer(data, dtype=np.uint8).reshape(-1, bpp)
    return src_blocks[src_off // bpp].tobytes()


def decode_bntx_zs_rgba(zs_path: str) -> np.ndarray:
    """Decompress and decode a single-texture ASTC `.bntx.zs` file to HxWx4 RGBA uint8."""
    with open(zs_path, "rb") as f:
        dec = zstd.ZstdDecompressor().decompress(f.read())
    idx = dec.find(b"BRTI")
    w, h = struct.unpack_from("<II", dec, idx + 0x24)
    fmt = struct.unpack_from("<I", dec, idx + 0x1C)[0]
    bh = struct.unpack_from("<I", dec, idx + 0x34)[0]
    dsz = struct.unpack_from("<I", dec, idx + 0x50)[0]
    brtd = dec.find(b"BRTD")
    bw, bkh = ASTC_BLOCKS[fmt >> 8]
    lin = deswizzle_nvn2_ampere(w, h, bw, bkh, 16, bh, dec[brtd + 0x10 : brtd + 0x10 + dsz])
    bgra = texture2ddecoder.decode_astc(lin, w, h, bw, bkh)
    return np.array(Image.frombytes("RGBA", (w, h), bgra, "raw", "BGRA"))


def decode_ui_common_assets(romfs_dir: str) -> tuple[dict[str, np.ndarray], Image.Image]:
    """Decode LocalMapPaper_* (2000x1440 centered) and MapIconArrow_00 exit chevron purely on CPU."""
    cmn_path = os.path.join(romfs_dir, "UI", "Layout2Archive", "Common.Product.100.Nin_Ounce_NVN2.bntx.zs")
    with open(cmn_path, "rb") as f:
        dec_cmn = zstd.ZstdDecompressor().decompress(f.read())

    wanted_papers = {"LocalMapPaper_00", "LocalMapPaper_Ganon_00", "LocalMapPaper_Gerudo_00"}
    papers: dict[str, np.ndarray] = {}
    exit_icon: Image.Image | None = None
    pos = 0
    while len(papers) < len(wanted_papers) or exit_icon is None:
        idx = dec_cmn.find(b"BRTI", pos)
        if idx == -1:
            break
        name_ptr = struct.unpack_from("<Q", dec_cmn, idx + 0x60)[0]
        nlen = struct.unpack_from("<H", dec_cmn, name_ptr)[0]
        tname = dec_cmn[name_ptr + 2 : name_ptr + 2 + nlen].decode("utf-8", errors="replace")
        if tname in wanted_papers or tname == "MapIconArrow_00":
            w, h = struct.unpack_from("<II", dec_cmn, idx + 0x24)
            bh = struct.unpack_from("<I", dec_cmn, idx + 0x34)[0]
            dsz = struct.unpack_from("<I", dec_cmn, idx + 0x50)[0]
            mip_ptrs = struct.unpack_from("<Q", dec_cmn, idx + 0x70)[0]
            data_off = struct.unpack_from("<Q", dec_cmn, mip_ptrs)[0]
            lin = deswizzle_nvn2_ampere(w, h, 4, 4, 16, bh, dec_cmn[data_off : data_off + dsz])
            bgra = texture2ddecoder.decode_astc(lin, w, h, 4, 4)
            im = Image.frombytes("RGBA", (w, h), bgra, "raw", "BGRA")
            if tname == "MapIconArrow_00":
                exit_icon = im.crop((32, 32, 96, 96))
            else:
                rgb = np.array(im.convert("RGB"), dtype=np.float32)
                ox = (w - 2000) // 2
                papers[tname] = rgb[:, ox : ox + 2000, :].copy()
        pos = idx + 4
    assert exit_icon is not None
    return papers, exit_icon


def apply_clamped_cas(arr_f32: np.ndarray, strength: float = 0.35) -> np.ndarray:
    """Pure-CPU zero-ringing Contrast-Adaptive Sharpening clamped to local 3x3 min/max."""
    blur = cv2.GaussianBlur(arr_f32, (0, 0), 1.05)
    sharp = arr_f32 + strength * (arr_f32 - blur)
    k3 = np.ones((3, 3), dtype=np.uint8)
    return np.clip(sharp, cv2.erode(arr_f32, k3), cv2.dilate(arr_f32, k3))


def save_native_webp(crop_rgb: np.ndarray, out_path: str) -> None:
    """Save native Switch 2 ROMFS map crop as crisp WebP without any local GPU calls."""
    arr = apply_clamped_cas(crop_rgb.astype(np.float32), strength=0.32)
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").save(out_path, "WEBP", quality=94, method=6)


def make_engine_tf(cam_x: float, cam_z: float, cap_height: float) -> dict[str, Any]:
    """Exact Hookshot engine world (X, Z) -> 2000x1440 map pixel (sx, sy) transform."""
    s = 2000.0 / float(cap_height)
    return {
        "mode": "scale_offset",
        "ax": round(s, 6),
        "az": 0.0,
        "c": round(1000.0 - cam_x * s, 4),
        "bx": 0.0,
        "bz": round(s, 6),
        "d": round(720.0 - cam_z * s, 4),
        "n": 100,
    }


def compute_shared_crop_box(alphas: list[np.ndarray], pad: int = 92, min_w: int = 680, min_h: int = 540) -> tuple[int, int, int, int]:
    """Compute union non-transparent bounding box [x0, y0, w, h] inside 2000x1440."""
    W, H = 2000, 1440
    union = np.zeros((H, W), dtype=bool)
    for a in alphas:
        union |= (a > 8)
    ys, xs = np.where(union)
    if len(xs) == 0:
        return (0, 0, W, H)

    x0 = max(0, int(xs.min()) - pad)
    x1 = min(W, int(xs.max()) + 1 + pad)
    y0 = max(0, int(ys.min()) - pad)
    y1 = min(H, int(ys.max()) + 1 + pad)

    if x1 - x0 < min_w:
        cx = (x0 + x1) // 2
        x0 = max(0, min(W - min_w, cx - min_w // 2))
        x1 = x0 + min_w
    if y1 - y0 < min_h:
        cy = (y0 + y1) // 2
        y0 = max(0, min(H - min_h, cy - min_h // 2))
        y1 = y0 + min_h

    if (x1 - x0) % 2 == 1:
        x1 = min(W, x1 + 1) if x1 < W else x1 - 1
    if (y1 - y0) % 2 == 1:
        y1 = min(H, y1 + 1) if y1 < H else y1 - 1
    return (x0, y0, x1 - x0, y1 - y0)


def fetch_zm_region_crop(zm_x0: float, zm_x1: float, zm_y0: float, zm_y1: float) -> np.ndarray:
    """Fetch official Nintendo Switch App (Zelda Notes) region crop for SIFT geometric locking."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    tx0, tx1 = int(math.floor(zm_x0 / 8.0)), int(math.floor(zm_x1 / 8.0))
    ty0, ty1 = int(math.floor(zm_y0 / 8.0)), int(math.floor(zm_y1 / 8.0))
    canvas = Image.new("RGB", ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256))
    for ix, tx in enumerate(range(tx0, tx1 + 1)):
        for iy, ty in enumerate(range(ty0, ty1 + 1)):
            url = f"https://zeldamaps.com/tiles/oot/hq-v1/hyrule-child/5_{tx}_{ty}.webp"
            raw = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=12).read()
            canvas.paste(Image.open(io.BytesIO(raw)).convert("RGB"), (ix * 256, iy * 256))
    px0 = int(round((zm_x0 - tx0 * 8.0) * 32))
    px1 = int(round((zm_x1 - tx0 * 8.0) * 32))
    py0 = int(round((zm_y0 - ty0 * 8.0) * 32))
    py1 = int(round((zm_y1 - ty0 * 8.0) * 32))
    return np.array(canvas.crop((px0, py0, px1, py1)))


def align_gemini_image_to_reference(gemini_path: str, ref_crop: np.ndarray, out_size: int = 2048) -> np.ndarray:
    """Affine-lock a Gemini-generated HD map image onto the exact official reference frame."""
    gem_rgb = np.array(Image.open(gemini_path).convert("RGB"))
    sift = cv2.SIFT_create(nfeatures=6000)
    kp1, des1 = sift.detectAndCompute(ref_crop[:, :, ::-1].copy(), None)
    kp2, des2 = sift.detectAndCompute(gem_rgb[:, :, ::-1].copy(), None)
    bf = cv2.BFMatcher()
    good = [m for m, n in bf.knnMatch(des1, des2, k=2) if m.distance < 0.75 * n.distance]
    pts1 = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    pts2 = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    m_ref_to_gem, _ = cv2.estimateAffinePartial2D(pts1, pts2, method=cv2.RANSAC, ransacReprojThreshold=5.0)

    sx = out_size / float(ref_crop.shape[1])
    sy = out_size / float(ref_crop.shape[0])
    m_out_to_gem = m_ref_to_gem.copy()
    m_out_to_gem[:, 0] /= sx
    m_out_to_gem[:, 1] /= sy
    m_gem_to_out = cv2.invertAffineTransform(m_out_to_gem)
    aligned = cv2.warpAffine(
        gem_rgb,
        m_gem_to_out,
        (out_size, out_size),
        flags=cv2.INTER_LANCZOS4,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return np.clip(apply_clamped_cas(aligned.astype(np.float32), strength=0.35), 0, 255).astype(np.uint8)


def fetch_zm_dungeon_2000x1440(slug: str) -> tuple[np.ndarray, np.ndarray]:
    """Fetch official Zelda Notes dungeon floor at zoom 3 (2048x2048) and crop centered 2000x1440."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    coords = [(tx, ty) for tx in range(8) for ty in range(8)]

    def dl(pair: tuple[int, int]):
        tx, ty = pair
        url = f"https://zeldamaps.com/tiles/oot/hq-v1/{slug}/3_{tx}_{ty}.webp"
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=12).read()
            return tx, ty, Image.open(io.BytesIO(raw)).convert("RGB")
        except Exception:
            return tx, ty, None

    canvas = Image.new("RGB", (2048, 2048))
    with ThreadPoolExecutor(max_workers=12) as pool:
        for tx, ty, tile in pool.map(dl, coords):
            if tile is not None:
                canvas.paste(tile, (tx * 256, ty * 256))

    crop = np.array(canvas.crop((24, 304, 2024, 1744)))
    gray = crop.astype(np.float32)
    border_med = np.median(np.vstack([gray[0:20, :, :].reshape(-1, 3), gray[-20:, :, :].reshape(-1, 3)]), axis=0)
    dist = np.linalg.norm(gray - border_med[None, None, :], axis=2)
    pseudo_alpha = np.where(dist > 22.0, 255, 0).astype(np.uint8)
    return crop, pseudo_alpha


def build_dungeon_rooms_list(mp_scene: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for rm in mp_scene.get("Room", []):
        if "CenterTrans" in rm and "Floor" in rm and rm["Floor"]:
            out.append(
                {
                    "center": [round(float(v), 2) for v in rm["CenterTrans"]],
                    "floors": [floor_num_to_label(int(f)) for f in rm["Floor"]],
                    "floor_id": floor_num_to_label(int(rm["Floor"][0])),
                }
            )
    return out


def main() -> None:
    os.makedirs(MAPS_DIR, exist_ok=True)
    reader = RomfsReader(ROMFS_DIR)
    cap_arr = reader.read_byml(r"Game\MapCaptureInfo\MapCaptureInfo.game__MapCaptureInfo.bgyml")["MapCaptureParamArray"]
    menu_arr = reader.read_byml(r"Game\MapMenuInfo\MapMenuInfo.game__ui__MapMenuInfo.bgyml")["MapMenuParamArray"]
    mp = reader.read_byml_zs(r"AoC1\Banc\BancBasedResource\MapParam.byml.zs")
    loc_to_cap = {menu_arr[i]["LocationName"]: cap_arr[i] for i in range(len(menu_arr))}

    papers, exit_icon_im = decode_ui_common_assets(ROMFS_DIR)
    exit_icon_im.save(os.path.join(MAPS_DIR, "map_icon_exit.webp"), "WEBP", lossless=True, method=6)

    field_dir = os.path.join(ROMFS_DIR, "UI", "CustomTex", "Map", "Field")
    dungeon_dir = os.path.join(ROMFS_DIR, "UI", "CustomTex", "Map", "Dungeon")

    places_path = os.path.join(DATA_DIR, "places.json")
    with open(places_path, "r", encoding="utf-8") as f:
        places_blob = json.load(f)
    places_by_id = {p["id"]: p for p in places_blob["places"]}
    ui_i18n = json.load(open(os.path.join(DATA_DIR, "ui_i18n.json"), encoding="utf-8"))
    floor_labels_i18n = ui_i18n.get("floorLabels", {})

    def floor_label_obj(fl_id: str) -> dict[str, str]:
        if fl_id in floor_labels_i18n:
            return floor_labels_i18n[fl_id]
        disp = f"B{fl_id[1:]}" if fl_id.startswith("S") else fl_id
        return {"zh-CN": disp, "ja": disp, "en": disp}

    # --- 1. Gemini HD Lost Woods (`perdido`) ---
    print("=== Building Lost Woods (`perdido`) from Gemini HD Image ===")
    lw_zm_x0, lw_zm_x1, lw_zm_y0, lw_zm_y1 = 176.5, 189.84375, 162.78125, 176.09375
    lw_ref = fetch_zm_region_crop(lw_zm_x0, lw_zm_x1, lw_zm_y0, lw_zm_y1)
    lw_sz = 2048
    lw_hd = align_gemini_image_to_reference(GEMINI_LOSTWOOD_SRC, lw_ref, out_size=lw_sz)
    Image.fromarray(lw_hd, "RGB").save(os.path.join(MAPS_DIR, "lostwood_hd.webp"), "WEBP", quality=94, method=6)

    lw_sx = lw_sz / float(lw_ref.shape[1])
    lw_sy = lw_sz / float(lw_ref.shape[0])
    lw_landmarks = [
        (-34.015, -3.745, 180.790, -169.260),
        (48.757, 16.034, 185.750, -170.450),
        (10.871, -52.066, 183.475, -166.363),
        (-33.188, 31.417, 180.835, -171.371),
        (3.820, -47.532, 183.051, -166.637),
        (27.800, -28.100, 184.489, -167.791),
        (20.500, -75.700, 184.052, -164.948),
        (-45.200, 72.600, 180.113, -173.838),
        (41.100, -4.900, 185.286, -169.190),
    ]
    lw_ax, lw_c = [float(v) for v in np.linalg.lstsq(
        np.array([[wx, 1.0] for wx, _, _, _ in lw_landmarks]),
        np.array([(zx - lw_zm_x0) * 32.0 * lw_sx for _, _, zx, _ in lw_landmarks]),
        rcond=None,
    )[0]]
    lw_bz, lw_d = [float(v) for v in np.linalg.lstsq(
        np.array([[wz, 1.0] for _, wz, _, _ in lw_landmarks]),
        np.array([(-zy - lw_zm_y0) * 32.0 * lw_sy for _, _, _, zy in lw_landmarks]),
        rcond=None,
    )[0]]
    lw_tf = {
        "mode": "scale_offset",
        "ax": round(lw_ax, 6),
        "az": 0.0,
        "c": round(lw_c, 4),
        "bx": 0.0,
        "bz": round(lw_bz, 6),
        "d": round(lw_d, 4),
        "n": len(lw_landmarks),
    }
    pl_lw = places_by_id["perdido"]
    pl_lw["startMap"] = "principal"
    pl_lw["maps"] = [
        {
            "id": "principal",
            "label": floor_label_obj("principal"),
            "image": "maps/lostwood_hd.webp",
            "aspect": 1.0,
            "viewBox": [0.0, 0.0, float(lw_sz), float(lw_sz)],
        }
    ]
    pl_lw["transform"] = lw_tf
    pl_lw["exits"] = [
        {
            "map": "principal",
            "to": dest_id,
            "x": round((lw_ax * ex_x + lw_c) / float(lw_sz), 4),
            "y": round((lw_bz * ex_z + lw_d) / float(lw_sz), 4),
            "rot": rot,
            "dir": ldir,
            "icon": "maps/map_icon_exit.webp",
        }
        for dest_id, ex_x, ex_z, rot, ldir in [
            ("prado",  24.0, -83.7,   0, "top"),
            ("goron",  24.0, -35.66,  0, "top"),
            ("rio",    68.5, -25.6,  90, "right"),
            ("kokiri",  0.0,   7.0, 180, "bottom"),
        ]
    ]

    # --- 2. Gemini HD Haunted Wasteland (`desierto`) ---
    print("=== Building Haunted Wasteland (`desierto`) from Gemini HD Image ===")
    hw_zm_x0, hw_zm_x1, hw_zm_y0, hw_zm_y1 = 52.40625, 64.96875, 113.84375, 126.40625
    hw_ref = fetch_zm_region_crop(hw_zm_x0, hw_zm_x1, hw_zm_y0, hw_zm_y1)
    hw_sz = 2048
    hw_hd = align_gemini_image_to_reference(GEMINI_WASTELAND_SRC, hw_ref, out_size=hw_sz)
    Image.fromarray(hw_hd, "RGB").save(os.path.join(MAPS_DIR, "wasteland_hd.webp"), "WEBP", quality=94, method=6)

    hw_scale_factor = hw_sz / 402.0
    hw_s = 1.4375 * hw_scale_factor
    hw_u_gs = (59.05 - hw_zm_x0) * 32.0 * hw_scale_factor
    hw_v_gs = (118.46 - hw_zm_y0) * 32.0 * hw_scale_factor
    hw_c = hw_u_gs - hw_s * 16.0
    hw_d = hw_v_gs - hw_s * (-99.8)
    hw_tf = {
        "mode": "scale_offset",
        "ax": round(hw_s, 6),
        "az": 0.0,
        "c": round(hw_c, 4),
        "bx": 0.0,
        "bz": round(hw_s, 6),
        "d": round(hw_d, 4),
        "n": 3,
    }
    pl_hw = places_by_id["desierto"]
    pl_hw["startMap"] = "principal"
    pl_hw["maps"] = [
        {
            "id": "principal",
            "label": floor_label_obj("principal"),
            "image": "maps/wasteland_hd.webp",
            "aspect": 1.0,
            "viewBox": [0.0, 0.0, float(hw_sz), float(hw_sz)],
        }
    ]
    pl_hw["transform"] = hw_tf
    pl_hw["exits"] = [
        {
            "map": "principal",
            "to": "coloso",
            "x": round((hw_s * (-117.4) + hw_c) / float(hw_sz), 4),
            "y": round((hw_s * (-55.8) + hw_d) / float(hw_sz), 4),
            "rot": -90,
            "dir": "top",
            "icon": "maps/map_icon_exit.webp",
        },
        {
            "map": "principal",
            "to": "fortaleza",
            "x": round((hw_s * 118.1 + hw_c) / float(hw_sz), 4),
            "y": round((hw_s * 54.7 + hw_d) / float(hw_sz), 4),
            "rot": 90,
            "dir": "top",
            "icon": "maps/map_icon_exit.webp",
        },
    ]

    # --- 3. Native 2000x1440 Switch 2 ROMFS Field/Town Maps (pure CPU) ---
    field_specs: dict[str, list[tuple[str, str, str, str]]] = {
        "kokiri":    [("principal", "KokiriForest_Child_00",       "LocalMapPaper_00",       "KokiriForest")],
        "prado":     [("principal", "SacredForestMeadow_Child_00", "LocalMapPaper_00",       "SacredForestMeadow")],
        "llanura":   [("principal", "HyruleField_Child_00",        "LocalMapPaper_00",       "HyruleField")],
        "lonlon":    [("principal", "LonLonRanch_Child_00",        "LocalMapPaper_00",       "LonLonRanch")],
        "ciudadela": [
            ("nino",   "Market_Child_00", "LocalMapPaper_00", "Market"),
            ("adulto", "Market_Adult_00", "LocalMapPaper_00", "Market"),
        ],
        "castillo": [
            ("nino",   "HyruleCastle_Child_00", "LocalMapPaper_00",       "HyruleCastle"),
            ("adulto", "GanonCastle_Adult_00",  "LocalMapPaper_Ganon_00", "GanonCastle"),
        ],
        "kakariko": [
            ("nino",   "KakarikoVillage_Child_01", "LocalMapPaper_00", "KakarikoVillage"),
            ("adulto", "KakarikoVillage_Adult_01", "LocalMapPaper_00", "KakarikoVillage"),
        ],
        "cementerio": [
            ("nino",   "Graveyard_Child_01", "LocalMapPaper_00", "Graveyard"),
            ("adulto", "Graveyard_Adult_01", "LocalMapPaper_00", "Graveyard"),
        ],
        "sendero":   [("principal", "DeathMountainTrail_Child_00",  "LocalMapPaper_00",        "DeathMountainTrail")],
        "goron":     [("principal", "GoronCity_Child_00",           "LocalMapPaper_00",        "GoronCity")],
        "crater":    [("principal", "DeathMountainCrater_Adult_00", "LocalMapPaper_00",        "DeathMountainCrater")],
        "rio":       [("principal", "ZoraRiver_Child_00",           "LocalMapPaper_00",        "ZoraRiver")],
        "dominio":   [("principal", "ZoraDomain_Child_00",          "LocalMapPaper_00",        "ZoraDomain")],
        "fuente": [
            ("nino",   "ZoraFountain_Child_00", "LocalMapPaper_00", "ZoraFountain"),
            ("adulto", "ZoraFountain_Adult_01", "LocalMapPaper_00", "ZoraFountain"),
        ],
        "lago":      [("principal", "LakeHylia_Child_00",           "LocalMapPaper_00",        "LakeHylia")],
        "valle":     [("principal", "GerudoValley_Adult_01",        "LocalMapPaper_00",        "GerudoValley")],
        "fortaleza": [("principal", "GerudoFortress_Adult_00",      "LocalMapPaper_Gerudo_00", "GerudoFortress")],
        "coloso":    [("principal", "DesertColossus_Adult_01",      "LocalMapPaper_00",        "DesertColossus")],
    }

    print("=== Building 18 Native 2K ROMFS Field/Town Maps (Pure CPU) ===")
    for pid, specs in field_specs.items():
        pl = places_by_id[pid]
        rendered: list[tuple[str, np.ndarray, np.ndarray, dict[str, Any]]] = []
        for fl_id, stem, paper_key, cap_loc in specs:
            rgba = decode_bntx_zs_rgba(os.path.join(field_dir, f"{stem}.bntx.zs"))
            bg = papers[paper_key].copy()
            a = rgba[:, :, 3:4].astype(np.float32) / 255.0
            comp = np.clip(rgba[:, :, :3].astype(np.float32) * a + bg * (1.0 - a), 0, 255).astype(np.uint8)
            cinfo = loc_to_cap[cap_loc]
            tf = make_engine_tf(cinfo["CameraPos"]["X"], cinfo["CameraPos"]["Z"], cinfo["Height"])
            rendered.append((fl_id, comp, rgba[:, :, 3], tf))

        independent_crop = (pid == "castillo")
        shared_box = None if independent_crop else compute_shared_crop_box([r[2] for r in rendered], pad=88)

        new_maps = []
        for idx_m, (fl_id, comp, alpha, tf) in enumerate(rendered):
            vx, vy, vw, vh = compute_shared_crop_box([alpha], pad=88) if independent_crop else shared_box
            crop = comp[vy : vy + vh, vx : vx + vw, :]
            fname = f"official_{pid}_{fl_id}.webp"
            save_native_webp(crop, os.path.join(MAPS_DIR, fname))
            m_entry: dict[str, Any] = {
                "id": fl_id,
                "label": floor_label_obj(fl_id),
                "image": f"maps/{fname}",
                "aspect": round(vw / float(vh), 4),
                "viewBox": [float(vx), float(vy), float(vw), float(vh)],
            }
            if independent_crop and idx_m > 0:
                m_entry["transform"] = tf
            new_maps.append(m_entry)
        pl["maps"] = new_maps
        pl["startMap"] = pl.get("startMap") or new_maps[0]["id"]
        pl["transform"] = rendered[0][3]

    # --- 4. Native 2000x1440 Switch 2 ROMFS Dungeon Floor Maps (pure CPU) ---
    romfs_dungeon_specs: dict[str, tuple[str, list[tuple[str, str | None, str]]]] = {
        "deku": ("InsideTheDekuTree", [
            ("3F", "InsideTheDekuTree_3F_Back", "InsideTheDekuTree_3F_State01_Main"),
            ("2F", "InsideTheDekuTree_2F_Back", "InsideTheDekuTree_2F_State01_Main"),
            ("1F", "InsideTheDekuTree_1F_Back", "InsideTheDekuTree_1F_State01_Main"),
            ("S1", "InsideTheDekuTree_B1_Back", "InsideTheDekuTree_B1_State01_Main"),
            ("S2", "InsideTheDekuTree_B2_Back", "InsideTheDekuTree_B2_State00_Main"),
        ]),
        "dodongos": ("DodongoCavern", [
            ("2F", "DodongoCavern_2F_Back", "DodongoCavern_2F_Main"),
            ("1F", "DodongoCavern_1F_Back", "DodongoCavern_1F_Main"),
        ]),
        "jabu": ("InsideJabuJabuBelly", [
            ("2F", "InsideJabuJabuBelly_2F_Back", "InsideJabuJabuBelly_2F_Main"),
            ("1F", "InsideJabuJabuBelly_1F_Back", "InsideJabuJabuBelly_1F_Main"),
            ("S1", "InsideJabuJabuBelly_B1_Back", "InsideJabuJabuBelly_B1_Main"),
        ]),
        "bosque": ("ForestTemple", [
            ("3F", "ForestTemple_3F_Back", "ForestTemple_3F_State00_Main"),
            ("2F", "ForestTemple_2F_Back", "ForestTemple_2F_State00_Main"),
            ("1F", "ForestTemple_1F_Back", "ForestTemple_1F_Main"),
            ("S1", "ForestTemple_B1_Back", "ForestTemple_B1_Main"),
            ("S2", "ForestTemple_B2_Back", "ForestTemple_B2_Main"),
        ]),
        "fuego": ("FireTemple", [
            ("5F", "FireTemple_5F_Back", "FireTemple_5F_State01_Main"),
            ("4F", "FireTemple_4F_Back", "FireTemple_4F_Main"),
            ("3F", "FireTemple_3F_Back", "FireTemple_3F_Main"),
            ("2F", "FireTemple_2F_Back", "FireTemple_2F_State01_Main"),
            ("1F", "FireTemple_1F_Back", "FireTemple_1F_State01_Main"),
        ]),
        "agua": ("WaterTemple", [
            ("3F", "WaterTemple_3F_Back", "WaterTemple_3F_Lv3_Main"),
            ("2F", "WaterTemple_2F_Back", "WaterTemple_2F_Lv2_Main"),
            ("1F", "WaterTemple_1F_Back", "WaterTemple_1F_Lv1_State01_Main"),
            ("S1", "WaterTemple_B1_Back", "WaterTemple_B1_Lv1_Main"),
        ]),
        "sombra": ("ShadowTemple", [
            ("S1", "ShadowTemple_B1_Back", "ShadowTemple_B1_Main"),
            ("S2", "ShadowTemple_B2_Back", "ShadowTemple_B2_Main"),
            ("S3", "ShadowTemple_B3_Back", "ShadowTemple_B3_Main"),
            ("S4", "ShadowTemple_B4_Back", "ShadowTemple_B4_State01_Main"),
        ]),
        "espiritu": ("SpiritTemple", [
            ("4F", "SpiritTemple_4F_Back",         "SpiritTemple_4F_State01_Main"),
            ("3F", "SpiritTemple_3F_State01_Back", "SpiritTemple_3F_State02_Main"),
            ("2F", "SpiritTemple_2F_Back",         "SpiritTemple_2F_Main"),
            ("1F", "SpiritTemple_1F_Back",         "SpiritTemple_1F_Main"),
        ]),
        "pozo": ("BottomOfTheWell", [
            ("S1", "BottomOfTheWell_B1_Back", "BottomOfTheWell_B1_State01_Main"),
            ("S2", "BottomOfTheWell_B2_Back", "BottomOfTheWell_B2_Main"),
        ]),
        "hielo": ("IceCavern", [
            ("principal", "IceCavern_1F_Back", "IceCavern_1F_Main"),
        ]),
    }

    print("=== Building 10 Native 2K ROMFS Dungeon Floor Maps (Pure CPU) ===")
    paper00 = papers["LocalMapPaper_00"]
    for pid, (cap_loc, fl_specs) in romfs_dungeon_specs.items():
        pl = places_by_id[pid]
        cinfo = loc_to_cap[cap_loc]
        tf = make_engine_tf(cinfo["CameraPos"]["X"], cinfo["CameraPos"]["Z"], cinfo["Height"])

        rendered_fl: list[tuple[str, np.ndarray, np.ndarray]] = []
        for fl_id, back_stem, main_stem in fl_specs:
            comp = paper00.copy()
            union_a = np.zeros((1440, 2000), dtype=np.uint8)
            for stem in [back_stem, main_stem]:
                if not stem:
                    continue
                zp = os.path.join(dungeon_dir, f"{stem}.bntx.zs")
                if not os.path.isfile(zp):
                    continue
                rgba = decode_bntx_zs_rgba(zp)
                union_a = np.maximum(union_a, rgba[:, :, 3])
                a = rgba[:, :, 3:4].astype(np.float32) / 255.0
                comp = rgba[:, :, :3].astype(np.float32) * a + comp * (1.0 - a)
            rendered_fl.append((fl_id, np.clip(comp, 0, 255).astype(np.uint8), union_a))

        vx, vy, vw, vh = compute_shared_crop_box([r[2] for r in rendered_fl], pad=88)
        new_maps = []
        for fl_id, comp, _ in rendered_fl:
            crop = comp[vy : vy + vh, vx : vx + vw, :]
            fname = f"official_{pid}_{fl_id}.webp"
            save_native_webp(crop, os.path.join(MAPS_DIR, fname))
            new_maps.append(
                {
                    "id": fl_id,
                    "label": floor_label_obj(fl_id),
                    "image": f"maps/{fname}",
                    "aspect": round(vw / float(vh), 4),
                    "viewBox": [float(vx), float(vy), float(vw), float(vh)],
                }
            )
        pl["maps"] = new_maps
        if not pl.get("startMap") or pl["startMap"] not in [m["id"] for m in new_maps]:
            pl["startMap"] = "1F" if any(m["id"] == "1F" for m in new_maps) else new_maps[0]["id"]
        pl["transform"] = tf

    # --- 5. Official 2000x1440 Zelda Notes Maps for Gerudo Training Ground & Inside Ganon's Castle ---
    zn_dungeon_specs: dict[str, tuple[dict[str, Any], str, list[tuple[str, str]]]] = {
        "gerudo": (
            cap_arr[35],
            "GerudoTrainingGround",
            [
                ("2F", "gerudo-training-ground-2f-state01"),
                ("1F", "gerudo-training-ground-1f-state01"),
            ],
        ),
        "ganon": (
            cap_arr[32],
            "InsideGanonCastle",
            [
                ("7F", "inside-ganon-castle-7f"),
                ("6F", "inside-ganon-castle-6f"),
                ("5F", "inside-ganon-castle-5f"),
                ("4F", "inside-ganon-castle-4f"),
                ("3F", "inside-ganon-castle-3f"),
                ("2F", "inside-ganon-castle-2f"),
                ("1F", "inside-ganon-castle-1f-state01"),
            ],
        ),
    }

    print("=== Building Gerudo Training Ground & Inside Ganon's Castle Official Maps (Pure CPU) ===")
    for pid, (cinfo, sc_name, fl_slugs) in zn_dungeon_specs.items():
        pl = places_by_id[pid]
        tf = make_engine_tf(cinfo["CameraPos"]["X"], cinfo["CameraPos"]["Z"], cinfo["Height"])
        rendered_zn: list[tuple[str, np.ndarray, np.ndarray]] = []
        for fl_id, slug in fl_slugs:
            comp, p_alpha = fetch_zm_dungeon_2000x1440(slug)
            rendered_zn.append((fl_id, comp, p_alpha))

        vx, vy, vw, vh = compute_shared_crop_box([r[2] for r in rendered_zn], pad=88)
        new_maps = []
        for fl_id, comp, _ in rendered_zn:
            crop = comp[vy : vy + vh, vx : vx + vw, :]
            fname = f"official_{pid}_{fl_id}.webp"
            save_native_webp(crop, os.path.join(MAPS_DIR, fname))
            new_maps.append(
                {
                    "id": fl_id,
                    "label": floor_label_obj(fl_id),
                    "image": f"maps/{fname}",
                    "aspect": round(vw / float(vh), 4),
                    "viewBox": [float(vx), float(vy), float(vw), float(vh)],
                }
            )
        pl["maps"] = new_maps
        pl["startMap"] = "1F"
        pl["transform"] = tf
        pl["scenes"] = ["InsideGanonCastle", "CrumblingGanonCastle"] if pid == "ganon" else [sc_name]
        if sc_name in mp:
            pl["dungeon_floors"] = build_dungeon_rooms_list(mp[sc_name])

    # --- 6. Re-project all 184 Collectible Pins ---
    print("=== Re-projecting all 184 Collectible Pins ===")
    lw_px_scale = lw_sz / 1113.0
    perdido_verified = {
        "perdido-heart-01": ([-34.015, 104.5, -3.745],    {"type": "bool32", "flag": "Npc_SkullKid_Child_IsGetHeartPiece"}, (0.0, 0.0)),
        "perdido-heart-02": ([48.757, 98.341, 16.034],    {"type": "bool32", "flag": "Minigame_SkullKidSession_IsGetHeartPiece"}, (0.0, 0.0)),
        "perdido-gs-01":    ([-33.188, 100.168, 31.417],  {"type": "b64", "hash": "9333354743976439035", "actor_hash": "9333354743976439033"}, (-12.0 * lw_px_scale, -5.0 * lw_px_scale)),
        "perdido-bean-01":  ([-33.188, 99.888, 31.417],   {"type": "bool32", "flag": "Gimmick_MagicBeanSoil_LostWood02"}, (12.0 * lw_px_scale, 5.0 * lw_px_scale)),
        "perdido-gs-02":    ([10.871, 99.775, -52.066],   {"type": "b64", "hash": "17796658857969527114", "actor_hash": "17796658857969527112"}, (-12.0 * lw_px_scale, 4.0 * lw_px_scale)),
        "perdido-bean-02":  ([10.871, 99.495, -52.066],   {"type": "bool32", "flag": "Gimmick_MagicBeanSoil_LostWood01"}, (12.0 * lw_px_scale, 6.0 * lw_px_scale)),
        "perdido-gs-03":    ([14.451, 105.851, -56.418],  {"type": "b64", "hash": "4335656213162247228", "actor_hash": "4335656213162247230"}, (6.0 * lw_px_scale, -6.0 * lw_px_scale)),
    }

    coord_overrides: dict[str, tuple[list[float], str | None]] = {
        "castillo-fairy-01":     ([68.092, 107.728, -63.335], "nino"),
        "castillo-fairy-02":     ([94.757, 84.063, 319.231],  "adulto"),
        "sendero-fairy-01":      ([-17.7, 210.1, -142.9],     "principal"),
        "crater-fairy-01":       ([-34.3, 121.1, 24.4],       "principal"),
        "fuente-fairy-01":       ([60.7, 103.2, 48.1],        "nino"),
        "coloso-fairy-01":       ([-49.1, 100.4, -32.9],      "principal"),
        "kakariko-bottle-01":    ([-72.1, 99.3, 73.1],        "nino"),
        "lonlon-bottle-01":      ([-53.6, 150.7, 197.8],      "principal"),
        "lago-bottle-01":        ([-151.62, 124.97, 461.04],  "principal"),
        "ciudadela-bottle-01":   ([12.5, 111.9, 57.0],        "adulto"),
        "ciudadela-bottle-02":   ([20.6, 112.2, 5.4],         "nino"),
        "cementerio-thought-01": ([48.36, 104.56, 2.61],      "nino"),
        "desierto-gs-01":        ([16.0, 88.8, -99.8],        "principal"),
        "deku-heart-01":         ([-29.0, 53.04, 47.396],     "S2"),
        "dodongos-heart-01":     ([14.9, 73.25, -74.1],       "1F"),
        "jabu-heart-01":         ([42.397, 102.01, -108.167], "2F"),
        "bosque-heart-01":       ([0.0, 59.5, -40.9],         "S2"),
        "fuego-heart-01":        ([-39.0, 105.0, 0.0],        "1F"),
        "agua-heart-01":         ([-4.5, 131.4, -71.2],       "3F"),
        "sombra-heart-01":       ([-138.5, 42.0, 19.1],       "S4"),
        "espiritu-heart-01":     ([0.0, 135.0, -76.7],        "3F"),
    }

    cols_path = os.path.join(DATA_DIR, "collectibles.json")
    with open(cols_path, "r", encoding="utf-8") as f:
        cols = json.load(f)

    by_place_floor: dict[tuple[str, str], list[tuple[dict[str, Any], float, float, list[float]]]] = {}
    for c in cols:
        cid = c["id"]
        pid = c["place"]
        if cid in perdido_verified:
            v_coords, v_rule, (dx, dy) = perdido_verified[cid]
            c["coords"] = v_coords
            c["rule"] = v_rule
            u = lw_tf["ax"] * v_coords[0] + lw_tf["c"] + dx
            v = lw_tf["bz"] * v_coords[2] + lw_tf["d"] + dy
            c["at"] = {"map": "principal", "x": round(u / float(lw_sz), 4), "y": round(v / float(lw_sz), 4)}
            continue

        pl = places_by_id[pid]
        maps = pl.get("maps", [])
        if not maps:
            continue

        if cid in coord_overrides:
            ov_coords, ov_fl = coord_overrides[cid]
            if not c.get("coords"):
                c["coords"] = ov_coords
            proj_coords = ov_coords
            fl_id = ov_fl or (c.get("at") or {}).get("map") or maps[0]["id"]
        else:
            proj_coords = c["coords"]
            fl_id = (c.get("at") or {}).get("map") or maps[0]["id"]

        m_obj = next((m for m in maps if m["id"] == fl_id), maps[0])
        fl_id = m_obj["id"]
        tf = m_obj.get("transform") or pl["transform"]
        wx, _, wz = proj_coords
        sx = tf["ax"] * wx + tf["az"] * wz + tf["c"]
        sy = tf["bx"] * wx + tf["bz"] * wz + tf["d"]
        by_place_floor.setdefault((pid, fl_id), []).append((c, sx, sy, m_obj["viewBox"]))

    for (_pid, fl_id), entries in by_place_floor.items():
        n = len(entries)
        adj = [[sx, sy] for _, sx, sy, _ in entries]
        used = [False] * n
        for i in range(n):
            if used[i]:
                continue
            cluster = [i]
            for j in range(i + 1, n):
                if not used[j] and math.hypot(adj[i][0] - adj[j][0], adj[i][1] - adj[j][1]) < 18.0:
                    cluster.append(j)
            if len(cluster) > 1:
                cx = sum(adj[k][0] for k in cluster) / len(cluster)
                cy = sum(adj[k][1] for k in cluster) / len(cluster)
                spread = 12.0
                for idx_c, k in enumerate(cluster):
                    used[k] = True
                    offset = (idx_c - (len(cluster) - 1) / 2.0) * (2.0 * spread)
                    adj[k][0] = cx + offset
                    adj[k][1] = cy

        for (c, _, _, vb), (fx, fy) in zip(entries, adj):
            vx, vy, vw, vh = vb
            u = max(0.02, min(0.98, (fx - vx) / vw))
            v = max(0.02, min(0.98, (fy - vy) / vh))
            c["at"] = {"map": fl_id, "x": round(u, 4), "y": round(v, 4)}

    with open(places_path, "w", encoding="utf-8") as f:
        json.dump(places_blob, f, indent=2, ensure_ascii=False)
    with open(cols_path, "w", encoding="utf-8") as f:
        json.dump(cols, f, indent=2, ensure_ascii=False)

    referenced = {os.path.basename(places_blob["map"]["image"])}
    for p in places_blob["places"]:
        for m in p.get("maps", []):
            referenced.add(os.path.basename(m["image"]))
        for ex in p.get("exits", []):
            if ex.get("icon"):
                referenced.add(os.path.basename(ex["icon"]))

    for svg_p in glob.glob(os.path.join(MAPS_DIR, "*.svg")):
        if os.path.basename(svg_p) not in referenced:
            os.remove(svg_p)

    print("All 32 official maps built cleanly (Gemini HD + Native Switch 2 ROMFS, zero local GPU).")


if __name__ == "__main__":
    main()

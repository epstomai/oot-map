"""Pure-Python parser for Switch 2 OoT Remake (Hookshot) progress.sav and caption.sav."""

from __future__ import annotations

import json
import math
import os
import struct
from datetime import datetime, timezone
from typing import Any

BOOL64_PTR_HASH = 0xA3DB7114


class CatalogStore:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        with open(os.path.join(data_dir, "collectibles.json"), "r", encoding="utf-8") as f:
            self.collectibles: list[dict[str, Any]] = json.load(f)
        with open(os.path.join(data_dir, "places.json"), "r", encoding="utf-8") as f:
            places_blob = json.load(f)
        self.overworld_map: dict[str, Any] = places_blob["map"]
        self.places: list[dict[str, Any]] = places_blob["places"]
        self.places_by_id: dict[str, dict[str, Any]] = {p["id"]: p for p in self.places}
        with open(os.path.join(data_dir, "categories.json"), "r", encoding="utf-8") as f:
            self.categories: list[dict[str, Any]] = json.load(f)
        with open(os.path.join(data_dir, "requirements.json"), "r", encoding="utf-8") as f:
            self.requirements: dict[str, dict[str, str]] = json.load(f)
        with open(os.path.join(data_dir, "ui_i18n.json"), "r", encoding="utf-8") as f:
            self.ui_i18n: dict[str, Any] = json.load(f)
        with open(os.path.join(data_dir, "gamedata_hashes.json"), "r", encoding="utf-8") as f:
            gd_blob = json.load(f)
        self.hashes: dict[str, int] = gd_blob["hashes"]
        self.b64_known_sample: set[int] = set(gd_blob.get("b64_known_sample", []))

        self.scene_to_place: dict[str, str] = {}
        for p in self.places:
            for sc in p.get("scenes", []):
                if sc not in self.scene_to_place:
                    self.scene_to_place[sc] = p["id"]
        self.scene_to_place["IngoRanch_Adult"] = "lonlon"
        self.scene_to_place["IngoRanch"] = "lonlon"
        self.scene_to_place["GanonCastle"] = "castillo"
        self.scene_to_place["GerudoTrainingGround"] = "gerudo"


def classify_hyrule_field_subplace(x: float, z: float) -> str:
    if -160.0 <= x <= -20.0 and 170.0 <= z <= 310.0:
        return "lonlon"
    if x <= -35.0 and z >= 360.0:
        return "lago"
    return "llanura"


def apply_tf(tf: dict[str, Any], x: float, z: float) -> tuple[float, float] | None:
    if not tf or tf.get("mode") == "none":
        return None
    return (
        tf["ax"] * x + tf["az"] * z + tf["c"],
        tf["bx"] * x + tf["bz"] * z + tf["d"],
    )


def resolve_place_and_floor(
    scene: str,
    pos: list[float] | None,
    is_child: bool,
    catalog: CatalogStore,
) -> tuple[str | None, str | None]:
    if not scene:
        return None, None
    if scene.startswith("HyruleField"):
        if pos and len(pos) >= 3:
            pid = classify_hyrule_field_subplace(pos[0], pos[2])
        else:
            pid = "llanura"
    else:
        pid = catalog.scene_to_place.get(scene)
        if not pid:
            base = scene.replace("_Child", "").replace("_Adult_Alternative", "").replace("_Adult", "")
            for candidate in catalog.places:
                for sc in candidate.get("scenes", []):
                    if sc.startswith(base):
                        pid = candidate["id"]
                        break
                if pid:
                    break
    if not pid:
        return None, None

    place = catalog.places_by_id.get(pid)
    if not place or not place.get("maps"):
        return pid, None

    map_ids = [m["id"] for m in place["maps"]]
    if "nino" in map_ids and "adulto" in map_ids:
        return pid, "nino" if is_child else "adulto"

    rooms = place.get("dungeon_floors") or []
    if rooms and pos and len(pos) >= 3:
        px, py, pz = pos[0], pos[1], pos[2]
        best_floor = None
        best_dist = 1e18
        for rm in rooms:
            cx, cy, cz = rm["center"]
            d = (px - cx) ** 2 + (pz - cz) ** 2 + 4.0 * (py - cy) ** 2
            if d < best_dist:
                best_dist = d
                for cand_fl in rm.get("floors", [rm.get("floor_id")]):
                    if cand_fl in map_ids:
                        best_floor = cand_fl
                        break
        if best_floor:
            return pid, best_floor

    return pid, place.get("startMap") or map_ids[0]


def project_player_positions(
    scene: str,
    place_id: str | None,
    floor_id: str | None,
    pos: list[float] | None,
    catalog: CatalogStore,
) -> dict[str, Any]:
    overworld_uv = None
    place_uv: dict[str, dict[str, float]] = {}

    if place_id and place_id in catalog.places_by_id:
        place = catalog.places_by_id[place_id]
        if scene.startswith(("HyruleField", "LonLonRanch", "LakeHylia", "IngoRanch")) and pos and len(pos) >= 3:
            res = apply_tf(catalog.overworld_map.get("overworld_hyrule_tf", {}), pos[0], pos[2])
            if res:
                overworld_uv = {
                    "x": round(max(0.02, min(0.98, res[0])), 4),
                    "y": round(max(0.02, min(0.98, res[1])), 4),
                }
        if overworld_uv is None and place.get("pin"):
            overworld_uv = {"x": place["pin"]["x"], "y": place["pin"]["y"]}

        if pos and len(pos) >= 3 and place.get("maps"):
            for m in place["maps"]:
                sxy = apply_tf(m.get("transform") or place.get("transform", {}), pos[0], pos[2])
                if sxy:
                    sx, sy = sxy
                    vx, vy, vw, vh = m.get("viewBox", [0.0, 0.0, 1000.0, 1000.0])
                    if vw > 0 and vh > 0:
                        u = (sx - vx) / vw
                        v = (sy - vy) / vh
                        place_uv[m["id"]] = {
                            "x": round(max(-0.08, min(1.08, u)), 4),
                            "y": round(max(-0.08, min(1.08, v)), 4),
                        }

    return {
        "overworld": overworld_uv,
        "place": place_uv,
        "active_place_uv": place_uv.get(floor_id) if floor_id else None,
    }


def extract_caption_thumbnail(caption_path: str) -> bytes | None:
    if not os.path.isfile(caption_path):
        return None
    try:
        with open(caption_path, "rb") as f:
            buf = f.read()
        idx = buf.find(b"\xff\xd8\xff")
        if idx == -1:
            return None
        eoi = buf.rfind(b"\xff\xd9")
        if eoi != -1 and eoi > idx:
            return buf[idx : eoi + 2]
        return buf[idx:]
    except OSError:
        return None


def parse_progress_sav(sav_path: str, catalog: CatalogStore) -> dict[str, Any]:
    with open(sav_path, "rb") as f:
        buf = f.read()
    if len(buf) < 0x30:
        raise ValueError(f"Save file too short: {sav_path}")
    magic = struct.unpack("<I", buf[0:4])[0]
    if magic != 0x01020304:
        raise ValueError(f"Unexpected progress.sav magic: 0x{magic:08x}")
    end_off = struct.unpack("<I", buf[8:12])[0]
    if end_off < 0x28 or end_off > len(buf):
        raise ValueError(f"Invalid end_off=0x{end_off:x} in {sav_path}")

    kv: dict[int, int] = {}
    for off in range(0x28, end_off, 8):
        h, v = struct.unpack("<II", buf[off : off + 8])
        kv[h] = v

    # Extract Bool64bitKey table via exact pointer hash (0xa3db7114)
    b64_set: set[int] = set()
    ptr = kv.get(BOOL64_PTR_HASH, 0)
    if end_off <= ptr < len(buf):
        pos = ptr
        while pos + 8 <= len(buf):
            q = struct.unpack("<Q", buf[pos : pos + 8])[0]
            if q == 0:
                break
            b64_set.add(q)
            pos += 8

    H = catalog.hashes

    def get_int(name: str, default: int = 0) -> int:
        h = H.get(name)
        if h is None:
            return default
        val = kv.get(h)
        if val is None:
            return default
        return struct.unpack("<i", struct.pack("<I", val))[0]

    def get_bool(name: str) -> bool:
        h = H.get(name)
        return bool(kv.get(h, 0)) if h is not None else False

    def get_float(name: str, default: float = 0.0) -> float:
        h = H.get(name)
        if h is None or h not in kv:
            return default
        return struct.unpack("<f", struct.pack("<I", kv[h]))[0]

    def get_str(name: str) -> str:
        h = H.get(name)
        if h is None:
            return ""
        off = kv.get(h, 0)
        if off == 0 or off >= len(buf):
            return ""
        end = buf.find(b"\x00", off, min(len(buf), off + 128))
        if end == -1:
            return ""
        return buf[off:end].decode("utf-8", errors="replace")

    def get_vec3(name: str) -> list[float] | None:
        h = H.get(name)
        if h is None:
            return None
        off = kv.get(h, 0)
        if off == 0 or off + 12 > len(buf):
            return None
        x, y, z = struct.unpack("<3f", buf[off : off + 12])
        if any(math.isnan(v) or math.isinf(v) for v in (x, y, z)):
            return None
        return [round(x, 3), round(y, 3), round(z, 3)]

    scene = get_str("Sequence_CurrentBanc")
    is_child = get_bool("Sequence_IsChildhood")
    pos = get_vec3("Player_Pos_For_Map")
    raw_rot = -get_float("Player_Rot_For_Map", 0.0)
    rot = 0.0 if abs(raw_rot) < 1e-6 else round(raw_rot, 2)

    place_id, floor_id = resolve_place_and_floor(scene, pos, is_child, catalog)
    projected = project_player_positions(scene, place_id, floor_id, pos, catalog)

    # Evaluate all 184 collectibles
    collected: dict[str, bool] = {}
    by_cat: dict[str, dict[str, int]] = {}
    for it in catalog.collectibles:
        iid = it["id"]
        rule = it["rule"]
        rtype = rule["type"]
        done = False
        if rtype == "b64":
            done = int(rule["hash"]) in b64_set
        elif rtype == "bool32":
            done = get_bool(rule["flag"])
        elif rtype == "bool32_any":
            done = any(get_bool(fl) for fl in rule["flags"])
        elif rtype == "int_gte":
            done = get_int(rule["flag"], 0) >= int(rule["target"])
        collected[iid] = done

        cat = it["cat"]
        bucket = by_cat.setdefault(cat, {"collected": 0, "total": 0})
        bucket["total"] += 1
        if done:
            bucket["collected"] += 1

    bottles_owned = sum(
        1
        for bid in (
            "kakariko-bottle-01",
            "lonlon-bottle-01",
            "lago-bottle-01",
            "ciudadela-bottle-01",
            "ciudadela-bottle-02",
        )
        if collected.get(bid)
    )

    life_q = get_int("PlayerStatus.Life", 12)
    max_life_q = get_int("PlayerStatus.MaxLife", 12)
    summary = {
        "hearts": round(life_q / 4.0, 2),
        "max_hearts": round(max_life_q / 4.0, 2),
        "heart_pieces_in_pouch": get_int("PouchData.Obj_Heart_Piece.StockNum", 0),
        "rupees": get_int("PlayerStatus.CurrentRupee", 0),
        "tokens": get_int("PouchData.Item_Token_Gold.StockNum", 0),
        "bottles": bottles_owned,
        "stones": {
            "kokiri": get_bool("IsGet.Item_Stone_Forest"),
            "goron": get_bool("IsGet.Item_Stone_Fire"),
            "zora": get_bool("IsGet.Item_Stone_Water"),
        },
        "medallions": {
            "light": get_bool("IsGet.Item_Medal_Light"),
            "forest": get_bool("IsGet.Item_Medal_Forest"),
            "fire": get_bool("IsGet.Item_Medal_Fire"),
            "water": get_bool("IsGet.Item_Medal_Water"),
            "shadow": get_bool("IsGet.Item_Medal_Shadow"),
            "spirit": get_bool("IsGet.Item_Medal_Spirit"),
        },
        "equipment": {
            "ocarina_fairy": get_bool("IsGet.Item_Ocarina_Fairy"),
            "ocarina_time": get_bool("IsGet.Item_Ocarina_Time"),
            "slingshot": get_bool("IsGet.Weapon_Range_SlingShot"),
            "boomerang": get_bool("IsGet.Item_Boomerang"),
            "bombs": get_bool("IsGet.Item_BombBag_Small"),
            "bow": get_bool("IsGet.Weapon_Range_Bow"),
            "hookshot": get_bool("IsGet.Item_Hookshot"),
            "longshot": get_bool("IsGet.Item_Longshot"),
            "hammer": get_bool("IsGet.Item_Hammer"),
            "lens": get_bool("IsGet.Armor_Adult_GlassTruth") or get_bool("IsGet.Armor_Child_GlassTruth") or get_bool("IsGet.Item_LensOfTruth"),
            "iron_boots": get_bool("IsGet.Armor_Adult_HeavyBoot"),
            "hover_boots": get_bool("IsGet.Armor_Adult_HoverBoot"),
            "goron_tunic": get_bool("IsGet.Armor_Adult_Goron"),
            "zora_tunic": get_bool("IsGet.Armor_Adult_Zora"),
            "silver_scale": get_bool("IsGet.Item_Scale_Silver"),
            "gold_scale": get_bool("IsGet.Item_Scale_Gold"),
            "goron_bracelet": get_bool("IsGet.Armor_Child_Gauntlet_Goron"),
            "silver_gauntlets": get_bool("IsGet.Armor_Adult_Gauntlet_Silver"),
            "gold_gauntlets": get_bool("IsGet.Armor_Adult_Gauntlet_Gold"),
            "mirror_shield": get_bool("IsGet.Weapon_Shield_Mirror"),
            "gerudo_token": get_bool("IsGet.Item_Token_Gerudo"),
        },
    }

    st = os.stat(sav_path)
    total_done = sum(1 for v in collected.values() if v)
    return {
        "save_path": sav_path,
        "mtime_ns": st.st_mtime_ns,
        "last_modified": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
        "player": {
            "scene": scene,
            "place": place_id,
            "floor": floor_id,
            "age": "child" if is_child else "adult",
            "pos": pos,
            "rot": rot,
            "projected": projected,
        },
        "summary": summary,
        "collected": collected,
        "counts": {
            "collected": total_done,
            "total": len(catalog.collectibles),
            "by_cat": by_cat,
        },
    }


def discover_profiles_and_slots(save_root: str, catalog: CatalogStore) -> dict[str, Any]:
    save_root = os.path.abspath(save_root) if save_root else ""
    profiles: list[dict[str, Any]] = []
    if not save_root or not os.path.isdir(save_root):
        return {"save_root": save_root, "exists": False, "profiles": []}

    def inspect_slot_dir(profile_id: str, slot_name: str, slot_dir: str) -> dict[str, Any] | None:
        sav_path = os.path.join(slot_dir, "progress.sav")
        if not os.path.isfile(sav_path):
            return None
        cap_path = os.path.join(slot_dir, "caption.sav")
        try:
            parsed = parse_progress_sav(sav_path, catalog)
            return {
                "profile": profile_id,
                "slot": slot_name,
                "slot_dir": slot_dir,
                "progress_path": sav_path,
                "has_thumbnail": extract_caption_thumbnail(cap_path) is not None,
                "mtime_ns": parsed["mtime_ns"],
                "last_modified": parsed["last_modified"],
                "scene": parsed["player"]["scene"],
                "place": parsed["player"]["place"],
                "age": parsed["player"]["age"],
                "tokens": parsed["summary"]["tokens"],
                "max_hearts": parsed["summary"]["max_hearts"],
                "collected_count": parsed["counts"]["collected"],
                "total_count": parsed["counts"]["total"],
            }
        except Exception as exc:
            st = os.stat(sav_path)
            return {
                "profile": profile_id,
                "slot": slot_name,
                "slot_dir": slot_dir,
                "progress_path": sav_path,
                "has_thumbnail": False,
                "mtime_ns": st.st_mtime_ns,
                "last_modified": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
                "error": str(exc),
            }

    # Case 1: save_root itself contains progress.sav
    if os.path.isfile(os.path.join(save_root, "progress.sav")):
        slot_info = inspect_slot_dir("direct", os.path.basename(save_root), save_root)
        if slot_info:
            profiles.append({"id": "direct", "path": save_root, "slots": [slot_info]})
        return {"save_root": save_root, "exists": True, "profiles": profiles}

    # Case 2: save_root directly contains slot_XX folders
    direct_slots = []
    for entry in sorted(os.listdir(save_root)):
        sub = os.path.join(save_root, entry)
        if os.path.isdir(sub) and os.path.isfile(os.path.join(sub, "progress.sav")):
            s = inspect_slot_dir("default", entry, sub)
            if s:
                direct_slots.append(s)
    if direct_slots:
        profiles.append({"id": "default", "path": save_root, "slots": direct_slots})
        return {"save_root": save_root, "exists": True, "profiles": profiles}

    # Case 3: save_root contains <profile_id>/slot_XX/progress.sav
    for entry in sorted(os.listdir(save_root)):
        prof_dir = os.path.join(save_root, entry)
        if not os.path.isdir(prof_dir):
            continue
        prof_slots = []
        for sub_name in sorted(os.listdir(prof_dir)):
            sub_dir = os.path.join(prof_dir, sub_name)
            if os.path.isdir(sub_dir) and os.path.isfile(os.path.join(sub_dir, "progress.sav")):
                s = inspect_slot_dir(entry, sub_name, sub_dir)
                if s:
                    prof_slots.append(s)
        if prof_slots:
            profiles.append({"id": entry, "path": prof_dir, "slots": prof_slots})

    return {"save_root": save_root, "exists": True, "profiles": profiles}

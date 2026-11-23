"""Builds master collectibles, places, transforms, and gamedata hash tables
from Nintendo Switch 2 Hookshot romfs + Nintenduo reference map data.
"""

from __future__ import annotations

import itertools
import json
import math
import os
import re
import sys
from typing import Any

import mmh3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from romfs_reader import RomfsReader, parse_msbt  # noqa: E402

ROMFS_DIR = r"F:\games\SwitchGames\hookshot\game\romfs"
MAP_ASSETS_DIR = r"H:\Codex Projs\OoT_Map\data\map_assets"
OUT_DIR = r"H:\Codex Projs\OoT_Map\data"

PLACE_TO_SCENE: dict[str, dict[str, Any]] = {
    "kokiri": {"loc_key": "KokiriForest", "banc_dirs": ["KokiriForest"], "scenes": ["KokiriForest_Child", "KokiriForest_Adult"]},
    "perdido": {"loc_key": "LostWood", "banc_dirs": ["LostWood"], "scenes": ["LostWood_Child", "LostWood_Adult"]},
    "prado": {"loc_key": "SacredForestMeadow", "banc_dirs": ["SacredForestMeadow"], "scenes": ["SacredForestMeadow_Child", "SacredForestMeadow_Adult"]},
    "llanura": {"loc_key": "HyruleField", "banc_dirs": ["HyruleField"], "scenes": ["HyruleField_Child", "HyruleField_Adult"]},
    "lonlon": {"loc_key": "LonLonRanch", "banc_dirs": ["HyruleField"], "scenes": ["LonLonRanch_Child", "LonLonRanch_Adult"]},
    "ciudadela": {"loc_key": "Market", "banc_dirs": ["Market"], "scenes": ["Market_Child", "Market_Adult"]},
    "templo": {"loc_key": "TimeTemple", "banc_dirs": ["TimeTemple"], "scenes": ["TimeTemple_Child", "TimeTemple_Adult"]},
    "castillo": {"loc_key": "HyruleCastle", "banc_dirs": ["HyruleCastle", "GanonCastle"], "scenes": ["HyruleCastle_Child", "HyruleCastle_Adult", "GanonCastle_Adult"]},
    "kakariko": {"loc_key": "KakarikoVillage", "banc_dirs": ["KakarikoVillage"], "scenes": ["KakarikoVillage_Child", "KakarikoVillage_Adult", "KakarikoVillage_Adult_Alternative"]},
    "cementerio": {"loc_key": "Graveyard", "banc_dirs": ["Graveyard"], "scenes": ["Graveyard_Child", "Graveyard_Adult"]},
    "sendero": {"loc_key": "DeathMountainTrail", "banc_dirs": ["DeathMountainTrail"], "scenes": ["DeathMountainTrail_Child", "DeathMountainTrail_Adult"]},
    "goron": {"loc_key": "GoronCity", "banc_dirs": ["GoronCity"], "scenes": ["GoronCity_Child", "GoronCity_Adult"]},
    "crater": {"loc_key": "DeathMountainCrater", "banc_dirs": ["DeathMountainCrater"], "scenes": ["DeathMountainCrater_Child", "DeathMountainCrater_Adult"]},
    "rio": {"loc_key": "ZoraRiver", "banc_dirs": ["ZoraRiver"], "scenes": ["ZoraRiver_Child", "ZoraRiver_Adult"]},
    "dominio": {"loc_key": "ZoraDomain", "banc_dirs": ["ZoraDomain"], "scenes": ["ZoraDomain_Child", "ZoraDomain_Adult", "ZoraDomain_Adult_Alternative"]},
    "fuente": {"loc_key": "ZoraFountain", "banc_dirs": ["ZoraFountain"], "scenes": ["ZoraFountain_Child", "ZoraFountain_Adult"]},
    "lago": {"loc_key": "LakeHylia", "banc_dirs": ["HyruleField"], "scenes": ["LakeHylia_Child", "LakeHylia_Adult"]},
    "valle": {"loc_key": "GerudoValley", "banc_dirs": ["GerudoValley"], "scenes": ["GerudoValley_Child", "GerudoValley_Adult"]},
    "fortaleza": {"loc_key": "GerudoFortress", "banc_dirs": ["GerudoFortress"], "scenes": ["GerudoFortress_Child", "GerudoFortress_Adult"]},
    "desierto": {"loc_key": "HountedWasteland", "banc_dirs": ["HountedWasteland"], "scenes": ["HountedWasteland_Child", "HountedWasteland_Adult"]},
    "coloso": {"loc_key": "DesertColossus", "banc_dirs": ["DesertColossus"], "scenes": ["DesertColossus_Child", "DesertColossus_Adult"]},
    "deku": {"loc_key": "InsideTheDekuTree", "banc_dirs": ["InsideTheDekuTree"], "scenes": ["InsideTheDekuTree"]},
    "dodongos": {"loc_key": "DodongoCavern", "banc_dirs": ["DodongoCavern"], "scenes": ["DodongoCavern"]},
    "jabu": {"loc_key": "InsideJabuJabuBelly", "banc_dirs": ["InsideJabuJabuBelly"], "scenes": ["InsideJabuJabuBelly"]},
    "bosque": {"loc_key": "ForestTemple", "banc_dirs": ["ForestTemple"], "scenes": ["ForestTemple"]},
    "fuego": {"loc_key": "FireTemple", "banc_dirs": ["FireTemple"], "scenes": ["FireTemple"]},
    "agua": {"loc_key": "WaterTemple", "banc_dirs": ["WaterTemple"], "scenes": ["WaterTemple"]},
    "sombra": {"loc_key": "ShadowTemple", "banc_dirs": ["ShadowTemple"], "scenes": ["ShadowTemple"]},
    "espiritu": {"loc_key": "SpiritTemple", "banc_dirs": ["SpiritTemple"], "scenes": ["SpiritTemple"]},
    "hielo": {"loc_key": "IceCavern", "banc_dirs": ["IceCavern"], "scenes": ["IceCavern"]},
    "pozo": {"loc_key": "BottomOfTheWell", "banc_dirs": ["BottomOfTheWell"], "scenes": ["BottomOfTheWell"]},
    "ganon": {"loc_key": "InsideGanonCastle", "banc_dirs": ["InsideGanonCastle"], "scenes": ["InsideGanonCastle"]},
}

BEAN_RULES: dict[str, dict[str, Any]] = {
    "kokiri-bean-01": {"type": "bool32", "flag": "IsPlantedMagicBean_SmallFarm.6092667454768667954"},
    "perdido-bean-01": {"type": "bool32", "flag": "IsPlantedMagicBean_SmallFarm.5234955674857122897"},
    "perdido-bean-02": {"type": "bool32", "flag": "IsPlantedMagicBean_SmallFarm.176409868210268833"},
    "cementerio-bean-01": {"type": "bool32", "flag": "IsPlantedMagicBean_SmallFarm.17500344509500247365"},
    "sendero-bean-01": {"type": "bool32", "flag": "IsPlantedMagicBean_SmallFarm.18350441421271687772"},
    "crater-bean-01": {"type": "bool32", "flag": "IsPlantedMagicBean_SmallFarm.12044463103654268862"},
    "rio-bean-01": {"type": "bool32", "flag": "IsPlantedMagicBean_SmallFarm.17092212646454540992"},
    "lago-bean-01": {"type": "bool32", "flag": "IsPlantedMagicBean_SmallFarm.6833516270248855649"},
    "valle-bean-01": {"type": "bool32", "flag": "IsPlantedMagicBean_SmallFarm.10857724324414230743"},
    "coloso-bean-01": {"type": "bool32", "flag": "IsPlantedMagicBean_SmallFarm.14429198438059673734"},
}

FAIRY_RULES: dict[str, dict[str, Any]] = {
    "castillo-fairy-01": {"type": "bool32_any", "flags": ["IsGet.Item_DinFire", "PouchData.Item_DinFire.StockNum"]},
    "sendero-fairy-01": {"type": "bool32_any", "flags": ["IsGet.Item_FairyBless_MP", "PouchData.Item_FairyBless_MP.StockNum"]},
    "crater-fairy-01": {"type": "bool32_any", "flags": ["IsGet.Item_FairyBless_MPDouble", "PouchData.Item_FairyBless_MPDouble.StockNum"]},
    "fuente-fairy-01": {"type": "bool32_any", "flags": ["IsGet.Item_FaroreWind", "PouchData.Item_FaroreWind.StockNum"]},
    "coloso-fairy-01": {"type": "bool32_any", "flags": ["IsGet.Item_NayruLove", "PouchData.Item_NayruLove.StockNum"]},
    "castillo-fairy-02": {"type": "bool32_any", "flags": ["IsGet.Item_FairyBless_DefenseDouble", "PouchData.Item_FairyBless_DefenseDouble.StockNum"]},
}

BOTTLE_RULES: dict[str, dict[str, Any]] = {
    "kakariko-bottle-01": {"type": "bool32", "flag": "MiniGame_CatchCucco_IsCompleted"},
    "lonlon-bottle-01": {"type": "bool32", "flag": "IsClear_Minigame_FindOutCucco"},
    "lago-bottle-01": {"type": "bool32_any", "flags": ["Get_StoneOfWater_GetRutoLetter", "IsGet.Item_Bottle_Letter"]},
    "ciudadela-bottle-01": {"type": "int_gte", "flag": "GhostShop_CouponNum", "target": 500},
    "ciudadela-bottle-02": {"type": "bool32_any", "flags": ["Market_Item_Bottle_TutorialEvent_Cleared", "Npc_Hylia_020_Shop_Item_Bottle_Present"]},
}

THOUGHT_TO_NOTE: dict[str, str] = {
    "cementerio-thought-01": "HrlField_Note_26",
    "cementerio-thought-02": "HrlField_Note_16",
    "coloso-thought-01": "HrlField_Note_25",
    "hielo-thought-01": "HrlField_Note_21",
    "lago-thought-01": "HrlField_Note_06",
    "llanura-thought-01": "HrlField_Note_04",
    "llanura-thought-02": "HrlField_Note_11",
    "llanura-thought-03": "HrlField_Note_12",
    "llanura-thought-04": "HrlField_Note_07",
    "llanura-thought-05": "HrlField_Note_15",
    "llanura-thought-06": "HrlField_Note_10",
    "llanura-thought-07": "HrlField_Note_08",
    "llanura-thought-08": "HrlField_Note_09",
    "llanura-thought-09": "HrlField_Note_02",
    "llanura-thought-10": "HrlField_Note_00",
    "lonlon-thought-01": "HrlField_Note_01",
    "pozo-thought-01": "HrlField_Note_23",
    "sendero-thought-01": "HrlField_Note_14",
    "sombra-thought-01": "HrlField_Note_24",
}


def classify_hyrule_field_subplace(x: float, z: float) -> str:
    if -160.0 <= x <= -20.0 and 170.0 <= z <= 310.0:
        return "lonlon"
    if x <= -35.0 and z >= 360.0:
        return "lago"
    return "llanura"


def read_svg_viewbox(svg_rel_path: str) -> list[float]:
    p = os.path.join(MAP_ASSETS_DIR, svg_rel_path.replace("/", os.sep))
    with open(p, "r", encoding="utf-8") as f:
        head = f.read(400)
    m = re.search(r'viewBox="([^"]+)"', head)
    if m:
        return [float(x) for x in m.group(1).split()]
    return [0.0, 0.0, 1000.0, 1000.0]


def fit_axis_scale_offset(pts_xz: list[tuple[float, float]], pts_uv: list[tuple[float, float]]) -> dict[str, Any]:
    n = len(pts_xz)
    if n == 0:
        return {"mode": "none", "ax": 1.0, "az": 0.0, "c": 0.0, "bx": 0.0, "bz": 1.0, "d": 0.0, "n": 0}
    if n == 1:
        x0, z0 = pts_xz[0]
        u0, v0 = pts_uv[0]
        return {"mode": "offset", "ax": 2.0, "az": 0.0, "c": u0 - 2.0 * x0, "bx": 0.0, "bz": 2.0, "d": v0 - 2.0 * z0, "n": 1}
    xs = [p[0] for p in pts_xz]
    zs = [p[1] for p in pts_xz]
    us = [p[0] for p in pts_uv]
    vs = [p[1] for p in pts_uv]
    mx, mz = sum(xs) / n, sum(zs) / n
    mu, mv = sum(us) / n, sum(vs) / n
    vx = sum((x - mx) ** 2 for x in xs)
    vz = sum((z - mz) ** 2 for z in zs)
    sx = sum((x - mx) * (u - mu) for x, u in zip(xs, us)) / vx if vx > 1.0 else None
    sz = sum((z - mz) * (v - mv) for z, v in zip(zs, vs)) / vz if vz > 1.0 else None
    if sx is not None and sx <= 0.0:
        sx = None
    if sz is not None and sz <= 0.0:
        sz = None
    if sx is None and sz is None:
        sx, sz = 4.0, 4.0
    elif sx is None:
        sx = sz
    elif sz is None:
        sz = sx
    elif abs(sx - sz) > 0.5 * max(sx, sz) and n <= 3:
        avg = (sx + sz) / 2.0
        sx = avg
        sz = avg
    return {"mode": "scale_offset", "ax": sx, "az": 0.0, "c": mu - sx * mx, "bx": 0.0, "bz": sz, "d": mv - sz * mz, "n": n}


def fit_affine_2d(pts_xz: list[tuple[float, float]], pts_uv: list[tuple[float, float]]) -> dict[str, Any]:
    n = len(pts_xz)
    if n < 3:
        return fit_axis_scale_offset(pts_xz, pts_uv)
    sxx = sum(x * x for x, _ in pts_xz)
    sxz = sum(x * z for x, z in pts_xz)
    szz = sum(z * z for _, z in pts_xz)
    sx = sum(x for x, _ in pts_xz)
    sz = sum(z for _, z in pts_xz)
    A = [[sxx, sxz, sx], [sxz, szz, sz], [sx, sz, float(n)]]
    bu = [sum(x * u for (x, _), (u, _) in zip(pts_xz, pts_uv)), sum(z * u for (_, z), (u, _) in zip(pts_xz, pts_uv)), sum(u for u, _ in pts_uv)]
    bv = [sum(x * v for (x, _), (_, v) in zip(pts_xz, pts_uv)), sum(z * v for (_, z), (_, v) in zip(pts_xz, pts_uv)), sum(v for _, v in pts_uv)]

    def solve_3x3(mat, rhs):
        M = [row[:] + [r] for row, r in zip(mat, rhs)]
        for col in range(3):
            piv = max(range(col, 3), key=lambda r: abs(M[r][col]))
            M[col], M[piv] = M[piv], M[col]
            if abs(M[col][col]) < 1e-12:
                return None
            div = M[col][col]
            for j in range(col, 4):
                M[col][j] /= div
            for r in range(3):
                if r != col:
                    f = M[r][col]
                    for j in range(col, 4):
                        M[r][j] -= f * M[col][j]
        return [M[i][3] for i in range(3)]

    cu = solve_3x3(A, bu)
    cv = solve_3x3(A, bv)
    if cu is None or cv is None:
        return fit_axis_scale_offset(pts_xz, pts_uv)
    det = cu[0] * cv[1] - cu[1] * cv[0]
    if (
        abs(det) < 1e-6
        or det < 0
        or cu[0] <= 0.3
        or cv[1] <= 0.3
        or abs(cu[1]) > 0.25 * abs(cu[0])
        or abs(cv[0]) > 0.25 * abs(cv[1])
    ):
        return fit_axis_scale_offset(pts_xz, pts_uv)
    return {"mode": "affine", "ax": cu[0], "az": cu[1], "c": cu[2], "bx": cv[0], "bz": cv[1], "d": cv[2], "n": n}


def apply_tf(tf: dict[str, Any], x: float, z: float) -> tuple[float, float]:
    return (tf["ax"] * x + tf["az"] * z + tf["c"], tf["bx"] * x + tf["bz"] * z + tf["d"])


def min_cost_match(items: list[dict], actors: list[dict], cost_fn) -> list[tuple[int, int, float]]:
    n = len(items)
    assert n == len(actors), f"Count mismatch: {n} items vs {len(actors)} actors"
    if n == 0:
        return []
    best_perm = None
    best_cost = 1e18
    for perm in itertools.permutations(range(n)):
        c = sum(cost_fn(items[i], actors[perm[i]]) for i in range(n))
        if c < best_cost:
            best_cost = c
            best_perm = perm
    assert best_perm is not None
    return [(i, best_perm[i], cost_fn(items[i], actors[best_perm[i]])) for i in range(n)]


def floor_num_to_label(floor_idx: int) -> str:
    if floor_idx >= 0:
        return f"{floor_idx + 1}F"
    return f"S{-floor_idx}"


def main():
    reader = RomfsReader(ROMFS_DIR)
    with open(os.path.join(MAP_ASSETS_DIR, "content.json"), "r", encoding="utf-8") as f:
        es_content = json.load(f)

    gd = reader.read_byml_zs(os.path.join("GameData", "GameDataList.Product.110.byml.zs"))["Data"]
    mp = reader.read_byml_zs(os.path.join("AoC1", "Banc", "BancBasedResource", "MapParam.byml.zs"))

    # Read viewBoxes for all maps in all places
    place_vbs: dict[str, dict[str, list[float]]] = {}
    for p in es_content["places"]:
        pid = p["id"]
        place_vbs[pid] = {}
        for m in p.get("maps", []):
            place_vbs[pid][m["id"]] = read_svg_viewbox(m["image"])

    def item_to_svg_xy(it: dict) -> tuple[float, float] | None:
        at = it.get("at")
        if not at:
            return None
        vbs = place_vbs.get(it["place"], {})
        vb = vbs.get(at["map"])
        if not vb:
            return None
        vx, vy, vw, vh = vb
        return (vx + at["x"] * vw, vy + at["y"] * vh)

    dir_to_place = {}
    for pid, info in PLACE_TO_SCENE.items():
        for bd in info["banc_dirs"]:
            if bd != "HyruleField":
                dir_to_place[bd] = pid

    skulls_by_place: dict[str, list[dict]] = {}
    containers_by_place: dict[str, list[dict]] = {}
    notes_by_name: dict[str, dict] = {}
    farms_by_key: dict[str, dict] = {}
    seen_skulls: set[int] = set()
    seen_containers: set[int] = set()

    banc_root = os.path.join(ROMFS_DIR, "Banc")
    for root_d, _, fns in os.walk(banc_root):
        if "MasterQuest" in root_d or "DreamWorld" in root_d:
            continue
        sdir = os.path.basename(root_d)
        for fn in sorted(fns):
            if not fn.endswith(".bcett.byml.zs") or "_MQ_" in fn:
                continue
            b = reader.read_byml_zs(os.path.relpath(os.path.join(root_d, fn), ROMFS_DIR), use_bcett=True)
            if not isinstance(b, dict):
                continue
            for a in b.get("Actors", []):
                g = a.get("Gyaml", "")
                tr = a.get("Translate", [0.0, 0.0, 0.0])
                h = a.get("Hash")
                dyn = a.get("Dynamic") or {}
                place = classify_hyrule_field_subplace(tr[0], tr[2]) if sdir == "HyruleField" else dir_to_place.get(sdir, sdir)
                if sdir == "GanonCastle":
                    place = "castillo"

                if g == "Enemy_Skulltula_Gold" and h not in seen_skulls:
                    seen_skulls.add(h)
                    skulls_by_place.setdefault(place, []).append({
                        "hash": h,
                        "token_hash": h ^ 2,
                        "tr": tr,
                        "place": place,
                        "file": fn,
                        "nocturnal": bool(dyn.get("Enemy_Skulltula_Gold_Nocturnal", False)),
                        "bean_soil": bool(dyn.get("Enemy_Skulltula_Gold_IsMagicBeanSoil", False)),
                    })
                elif g == "Obj_Heart_Container" and h not in seen_containers:
                    seen_containers.add(h)
                    containers_by_place.setdefault(place, []).append({
                        "hash": h,
                        "tr": tr,
                        "place": place,
                        "file": fn,
                    })
                elif g.startswith("HrlField_Note_") and g not in notes_by_name:
                    notes_by_name[g] = {"gyaml": g, "tr": tr, "place": place, "file": fn}
                elif g.startswith("Obj_SmallFarm") and "DiveInsectGameData" in dyn:
                    k = dyn["DiveInsectGameData"]
                    farm_info = {"flag": k, "hash": h, "tr": tr, "place": place, "file": fn}
                    if k not in farms_by_key:
                        farms_by_key[k] = farm_info
                    if h is not None:
                        plant_key = f"IsPlantedMagicBean_SmallFarm.{h}"
                        if plant_key not in farms_by_key:
                            farms_by_key[plant_key] = farm_info

    tbox_open_struct_hash = mmh3.hash("IsTreasureBoxOpen", signed=False)
    tbox_open_fields: set[int] = set()
    for st in gd.get("Struct", []):
        if isinstance(st, dict) and st.get("Hash") == tbox_open_struct_hash:
            for elem in st.get("DefaultValue", []):
                if isinstance(elem, dict) and "Hash" in elem:
                    tbox_open_fields.add(int(elem["Hash"]))

    hearts_by_place: dict[str, list[dict]] = {}
    seen_hearts: set[tuple[str, Any]] = set()
    for sc, val in sorted(mp.items()):
        if "_MQ" in sc:
            continue
        sc_base = sc.replace("_Child", "").replace("_Adult_Alternative", "").replace("_Adult", "")
        for ch in val.get("CollectHeart", []):
            ah = ch.get("ActorHash", 0)
            gdn = ch.get("GameDataHashName", "")
            if ah and mmh3.hash(str(ah), signed=False) in tbox_open_fields:
                key = ("b32", f"IsTreasureBoxOpen.{ah}")
            elif ah:
                key = ("b64", ah)
            else:
                key = ("b32", gdn)
            if key in seen_hearts:
                continue
            seen_hearts.add(key)
            place = next((pid for pid, info in PLACE_TO_SCENE.items() if info["loc_key"] == sc_base), sc_base)
            hearts_by_place.setdefault(place, []).append({
                "key_type": key[0],
                "key": key[1],
                "tr": ch["Trans"],
                "scene": sc,
                "place": place,
            })

    matched_rules: dict[str, dict[str, Any]] = {}
    matched_coords: dict[str, list[float]] = {}

    def normalize_pts(pts):
        xs = [p[0] for p in pts]
        zs = [p[1] for p in pts]
        minx, maxx = min(xs), max(xs)
        minz, maxz = min(zs), max(zs)
        rx = max(maxx - minx, 1e-3)
        rz = max(maxz - minz, 1e-3)
        return [((x - minx) / rx, (z - minz) / rz) for x, z in pts]

    for pid in [p["id"] for p in es_content["places"]]:
        for cat_name, pool in [("gs", skulls_by_place), ("heart", hearts_by_place), ("container", containers_by_place)]:
            n_items = [it for it in es_content["items"] if it["cat"] == cat_name and it["place"] == pid]
            a_items = pool.get(pid, [])
            if not n_items:
                continue
            if len(n_items) == 1:
                matches = [(0, 0, 0.0)]
            else:
                n_pts = [item_to_svg_xy(it) or (0.0, 0.0) for it in n_items]
                a_pts = [(a["tr"][0], a["tr"][2]) for a in a_items]
                n_norm = normalize_pts(n_pts)
                a_norm = normalize_pts(a_pts)
                n_idx = {id(n_items[i]): n_norm[i] for i in range(len(n_items))}
                a_idx = {id(a_items[i]): a_norm[i] for i in range(len(a_items))}

                def cost(it, act):
                    nx, ny = n_idx[id(it)]
                    ax, ay = a_idx[id(act)]
                    d = (nx - ax) ** 2 + (ny - ay) ** 2
                    if cat_name == "gs":
                        if bool(it.get("night")) != bool(act.get("nocturnal")):
                            d += 0.5
                        has_bugs = "bugs" in it.get("requires", [])
                        if has_bugs != bool(act.get("bean_soil")):
                            d += 0.8
                    return d

                matches = min_cost_match(n_items, a_items, cost)

            for ii, ai, _c in matches:
                it = n_items[ii]
                act = a_items[ai]
                matched_coords[it["id"]] = act["tr"]
                if cat_name == "gs":
                    matched_rules[it["id"]] = {"type": "b64", "hash": str(act["token_hash"]), "actor_hash": str(act["hash"])}
                elif cat_name == "container":
                    matched_rules[it["id"]] = {"type": "b64", "hash": str(act["hash"])}
                elif cat_name == "heart":
                    if act["key_type"] == "b64":
                        matched_rules[it["id"]] = {"type": "b64", "hash": str(act["key"])}
                    else:
                        matched_rules[it["id"]] = {"type": "bool32", "flag": act["key"]}

    for iid, rule in BEAN_RULES.items():
        matched_rules[iid] = rule
        if rule["type"] == "bool32" and rule["flag"] in farms_by_key:
            matched_coords[iid] = farms_by_key[rule["flag"]]["tr"]
        elif rule["type"] == "bool32_any":
            for fl in rule["flags"]:
                if fl in farms_by_key:
                    matched_coords[iid] = farms_by_key[fl]["tr"]
                    break
    for iid, rule in FAIRY_RULES.items():
        matched_rules[iid] = rule
    for iid, rule in BOTTLE_RULES.items():
        matched_rules[iid] = rule
    for iid, note_name in THOUGHT_TO_NOTE.items():
        num = note_name.split("_")[-1]
        matched_rules[iid] = {"type": "bool32", "flag": f"HaveReadHrlField_Note{num}"}
        if note_name in notes_by_name:
            matched_coords[iid] = notes_by_name[note_name]["tr"]

    # Fit (X, Z) -> shared SVG canvas (svg_x, svg_y) per place!
    transforms: dict[str, Any] = {}
    for p in es_content["places"]:
        pid = p["id"]
        if not p.get("maps"):
            transforms[pid] = {"mode": "none"}
            continue
        pts_xz = []
        pts_svg = []
        pt_ids = []
        for it in es_content["items"]:
            if it["place"] == pid and it["id"] in matched_coords:
                sxy = item_to_svg_xy(it)
                if not sxy:
                    continue
                tr = matched_coords[it["id"]]
                # Exclude Dampe/Royal Tomb interior items in Graveyard when fitting outdoor graveyard if needed
                if pid == "cementerio" and it["id"] in ("cementerio-thought-01", "cementerio-heart-01", "cementerio-heart-02"):
                    continue
                if pid == "kakariko" and it["id"] in ("kakariko-heart-02",):  # Windmill interior
                    continue
                if pid == "castillo" and it["id"] in ("castillo-gs-03", "castillo-fairy-02"):  # GanonCastle exterior
                    continue
                pts_xz.append((tr[0], tr[2]))
                pts_svg.append(sxy)
                pt_ids.append(it["id"])
        tf_so = fit_axis_scale_offset(pts_xz, pts_svg)
        tf_af = fit_affine_2d(pts_xz, pts_svg)
        if len(pts_xz) >= 4:
            err_so = max((math.hypot(apply_tf(tf_so, x, z)[0] - u, apply_tf(tf_so, x, z)[1] - v) for (x, z), (u, v) in zip(pts_xz, pts_svg)), default=0.0)
            err_af = max((math.hypot(apply_tf(tf_af, x, z)[0] - u, apply_tf(tf_af, x, z)[1] - v) for (x, z), (u, v) in zip(pts_xz, pts_svg)), default=0.0)
            tf = tf_af if err_af < err_so * 0.85 else tf_so
        else:
            tf = tf_so
        max_px = max((math.hypot(apply_tf(tf, x, z)[0] - u, apply_tf(tf, x, z)[1] - v) for (x, z), (u, v) in zip(pts_xz, pts_svg)), default=0.0)
        transforms[pid] = tf
        print(f"  TF {pid:12s} (n={len(pts_xz):2d}, {tf['mode']:12s}): max_svg_px_err={max_px:6.1f}")

    # Fit Overworld HyruleField (X, Z) -> hyrule.webp normalized (u, v)
    pins_by_id = {p["id"]: p["pin"] for p in es_content["places"] if "pin" in p}
    ow_pts_xz = [
        (0.007, 53.63),     # FrontOfMarket -> just south of ciudadela
        (210.85, 9.98),     # FrontOfKakariko -> west of kakariko
        (200.10, 309.06),   # FrontOfLostWoodBridge -> northwest of kokiri
        (-314.70, 160.83),  # FrontOfGerudoValley -> east of valle
        (-60.20, 180.50),   # LonLon entrance
        (-93.00, 398.00),   # LakeHylia entrance
        (-180.45, 493.63),  # OutsideOfWaterTemple -> agua
        (220.00, 140.74),   # FrontOfZoraRiver -> rio
    ]
    ow_pts_uv = [
        (pins_by_id["ciudadela"]["x"] + 0.015, pins_by_id["ciudadela"]["y"] + 0.050),
        (pins_by_id["kakariko"]["x"] - 0.025, pins_by_id["kakariko"]["y"] + 0.010),
        (pins_by_id["kokiri"]["x"] - 0.025, pins_by_id["kokiri"]["y"] - 0.010),
        (pins_by_id["valle"]["x"] + 0.035, pins_by_id["valle"]["y"] - 0.015),
        (pins_by_id["lonlon"]["x"], pins_by_id["lonlon"]["y"]),
        (pins_by_id["lago"]["x"], pins_by_id["lago"]["y"]),
        (pins_by_id["agua"]["x"], pins_by_id["agua"]["y"]),
        (pins_by_id["rio"]["x"], pins_by_id["rio"]["y"]),
    ]
    overworld_hf_tf = fit_axis_scale_offset(ow_pts_xz, ow_pts_uv)

    # Build dungeon floor room centers
    dungeon_floors: dict[str, list[dict]] = {}
    for pid, info in PLACE_TO_SCENE.items():
        sc = info["scenes"][0]
        if sc in mp and "Room" in mp[sc]:
            rooms = []
            for r in mp[sc]["Room"]:
                ct = r.get("CenterTrans")
                if not ct:
                    continue
                fl_raw = r.get("Floor", [0])
                fl_list = fl_raw if isinstance(fl_raw, list) else [fl_raw]
                if not fl_list:
                    fl_list = [0]
                rooms.append({
                    "floors": [floor_num_to_label(fi) for fi in fl_list],
                    "floor_id": floor_num_to_label(fl_list[0]),
                    "center": [round(v, 2) for v in ct],
                })
            dungeon_floors[pid] = rooms

    # Load official Mals LocationMsg/Location.msbt + en_content + i18n modules
    from romfs_reader import parse_msbt
    import i18n_core
    import i18n_items_part1
    import i18n_items_part2
    import i18n_items_part3

    loc_msgs = {
        lang: parse_msbt(reader.read_sarc_zs(f"Mals/{lang}.Product.110.sarc.zs")["LocationMsg/Location.msbt"])
        for lang in ("CNzh", "JPja", "USen")
    }
    with open(os.path.join(MAP_ASSETS_DIR, "en_content.json"), "r", encoding="utf-8") as f:
        en_content = json.load(f)

    zh_ja_items: dict[str, dict[str, tuple[str, str, str]]] = {}
    zh_ja_items.update(i18n_items_part1.ITEMS_ZH_JA_PART1)
    zh_ja_items.update(i18n_items_part2.ITEMS_ZH_JA_PART2)
    zh_ja_items.update(i18n_items_part3.ITEMS_ZH_JA_PART3)

    # Place official names (with custom disambiguation where Hyrule/Ganon or Nintenduo places split)
    place_name_overrides = {
        "castillo": {
            "zh-CN": "海拉鲁城堡 / 加侬城外",
            "ja": "ハイラル城 / ガノン城外周",
            "en": "Hyrule / Ganon's Castle",
        },
        "gerudo": {
            "zh-CN": loc_msgs["CNzh"].get("GerudoTrainingGround", "格鲁德训练场"),
            "ja": loc_msgs["JPja"].get("GerudoTrainingGround", "ゲルドの修練場"),
            "en": "Gerudo Training Ground",
        },
    }

    places_out = []
    for p in es_content["places"]:
        pid = p["id"]
        loc_key = PLACE_TO_SCENE.get(pid, {}).get("loc_key")
        if pid in place_name_overrides:
            names = place_name_overrides[pid]
        elif loc_key:
            names = {
                "zh-CN": loc_msgs["CNzh"].get(loc_key, pid),
                "ja": loc_msgs["JPja"].get(loc_key, pid),
                "en": en_content["places"].get(pid, {}).get("name") or loc_msgs["USen"].get(loc_key, pid),
            }
        else:
            names = {
                "zh-CN": p["name"],
                "ja": p["name"],
                "en": en_content["places"].get(pid, {}).get("name", p["name"]),
            }

        maps_out = []
        for m in p.get("maps", []):
            mid = m["id"]
            lbl = i18n_core.FLOOR_LABELS_I18N.get(mid, {"zh-CN": m["label"], "ja": m["label"], "en": m["label"]})
            maps_out.append({
                "id": mid,
                "label": lbl,
                "image": m["image"],
                "aspect": m.get("aspect"),
                "viewBox": place_vbs.get(pid, {}).get(mid, [0, 0, 1000, 1000]),
            })

        places_out.append({
            "id": pid,
            "kind": p.get("kind", "zone"),
            "region": p.get("region", ""),
            "region_i18n": i18n_core.REGIONS_I18N.get(p.get("region", ""), {"zh-CN": p.get("region", ""), "ja": p.get("region", ""), "en": p.get("region", "")}),
            "pin": p.get("pin"),
            "startMap": p.get("startMap"),
            "maps": maps_out,
            "scenes": PLACE_TO_SCENE.get(pid, {}).get("scenes", []),
            "transform": transforms.get(pid, {"mode": "none"}),
            "dungeon_floors": dungeon_floors.get(pid, []),
            "name": names,
            "intro": i18n_core.PLACES_INTRO_I18N.get(pid, {
                "zh-CN": "",
                "ja": "",
                "en": en_content["places"].get(pid, {}).get("intro", ""),
            }),
        })

    # Categories (exclude unused/empty 'key' if no items)
    used_cats = {it["cat"] for it in es_content["items"]}
    categories_out = []
    for c in es_content["categories"]:
        ckey = c["key"]
        if ckey not in used_cats:
            continue
        ci = i18n_core.CATEGORIES_I18N.get(ckey, {})
        categories_out.append({
            "key": ckey,
            "name": {
                "zh-CN": ci.get("zh-CN", {}).get("name", c["name"]),
                "ja": ci.get("ja", {}).get("name", c["name"]),
                "en": ci.get("en", {}).get("name", c["name"]),
            },
            "intro": {
                "zh-CN": ci.get("zh-CN", {}).get("intro", ""),
                "ja": ci.get("ja", {}).get("intro", ""),
                "en": ci.get("en", {}).get("intro", ""),
            },
        })

    # Requirements
    requirements_out = {}
    for req in es_content["requirements"]:
        rk = req["key"]
        ri = i18n_core.REQUIREMENTS_I18N.get(rk, {"zh-CN": req["name"], "ja": req["name"], "en": req["name"]})
        requirements_out[rk] = ri

    # Collectibles (184 items)
    collectibles_out = []
    missing_i18n = []
    missing_rules = []
    for it in es_content["items"]:
        iid = it["id"]
        en_it = en_content["items"].get(iid, {})
        zj = zh_ja_items.get(iid)
        if not zj:
            missing_i18n.append(iid)
            zh_t, zh_h, zh_g = en_it.get("name", it["name"]), en_it.get("hint", ""), en_it.get("desc", "")
            ja_t, ja_h, ja_g = en_it.get("name", it["name"]), en_it.get("hint", ""), en_it.get("desc", "")
        else:
            zh_t, zh_h, zh_g = zj["zh-CN"]
            ja_t, ja_h, ja_g = zj["ja"]

        en_t = en_it.get("name", it["name"])
        en_desc = en_it.get("desc", it.get("desc", ""))
        en_h = en_it.get("hint") or (en_desc.split("\n\n")[0][:140] if en_desc else "")

        rule = matched_rules.get(iid)
        if not rule:
            missing_rules.append(iid)

        collectibles_out.append({
            "id": iid,
            "n": it["n"],
            "cat": it["cat"],
            "place": it["place"],
            "at": it.get("at"),
            "age": "both" if it["cat"] == "bean" else it.get("age", "both"),
            "night": bool(it.get("night", False)),
            "requires": it.get("requires", []),
            "coords": [round(v, 3) for v in matched_coords[iid]] if iid in matched_coords else None,
            "rule": rule,
            "title": {"zh-CN": zh_t, "ja": ja_t, "en": en_t},
            "hint": {"zh-CN": zh_h, "ja": ja_h, "en": en_h},
            "guide": {"zh-CN": zh_g, "ja": ja_g, "en": en_desc},
        })

    assert not missing_i18n, f"Missing zh-CN/ja translations: {missing_i18n}"
    assert not missing_rules, f"Missing save rules: {missing_rules}"

    # Build gamedata_hashes.json for zero-romfs runtime save_parser & live_sync
    hash_names = [
        "Sequence_CurrentBanc",
        "Sequence_IsChildhood",
        "Sequence_IsInDreamWorld",
        "Sequence_ReservedDungeonRoomID",
        "Player_Pos_For_Map",
        "Player_Rot_For_Map",
        "PlayerStatus.Life",
        "PlayerStatus.MaxLife",
        "PlayerStatus.CurrentRupee",
        "PlayerStatus.EquipShield",
        "PlayerStatus.EquipArmor",
        "PouchData.Item_Token_Gold.StockNum",
        "PouchData.Obj_Heart_Piece.StockNum",
        "IsGet.Item_Stone_Forest",
        "IsGet.Item_Stone_Fire",
        "IsGet.Item_Stone_Water",
        "IsGet.Item_Medal_Light",
        "IsGet.Item_Medal_Forest",
        "IsGet.Item_Medal_Fire",
        "IsGet.Item_Medal_Water",
        "IsGet.Item_Medal_Shadow",
        "IsGet.Item_Medal_Spirit",
        "IsGet.Item_Ocarina_Fairy",
        "IsGet.Item_Ocarina_Time",
        "IsGet.Item_Hookshot",
        "IsGet.Item_Longshot",
        "IsGet.Weapon_Range_Bow",
        "IsGet.Weapon_Range_SlingShot",
        "IsGet.Item_Boomerang",
        "IsGet.Item_BombBag_Small",
        "IsGet.Item_Hammer",
        "IsGet.Armor_Adult_GlassTruth",
        "IsGet.Armor_Child_GlassTruth",
        "IsGet.Item_LensOfTruth",
        "IsGet.Armor_Adult_HeavyBoot",
        "IsGet.Armor_Adult_HoverBoot",
        "IsGet.Armor_Adult_Goron",
        "IsGet.Armor_Adult_Zora",
        "IsGet.Item_Scale_Silver",
        "IsGet.Item_Scale_Gold",
        "IsGet.Armor_Child_Gauntlet_Goron",
        "IsGet.Armor_Adult_Gauntlet_Silver",
        "IsGet.Armor_Adult_Gauntlet_Gold",
        "IsGet.Weapon_Shield_Deku",
        "IsGet.Weapon_Shield_Hylian",
        "IsGet.Weapon_Shield_Mirror",
        "IsGet.Weapon_Sword_Kokiri",
        "IsGet.Weapon_Sword_Master",
        "IsGet.Weapon_Sword_Biggoron",
        "IsGet.Item_DinFire",
        "IsGet.Item_FaroreWind",
        "IsGet.Item_NayruLove",
        "IsGet.Item_FairyBless_MP",
        "IsGet.Item_FairyBless_MPDouble",
        "IsGet.Item_FairyBless_DefenseDouble",
        "IsGet.Item_Token_Gerudo",
    ]
    for rule in matched_rules.values():
        if rule["type"] in ("bool32", "int_gte"):
            hash_names.append(rule["flag"])
        elif rule["type"] == "bool32_any":
            hash_names.extend(rule["flags"])

    hashes_map = {name: mmh3.hash(name, signed=False) for name in sorted(set(hash_names))}
    b64_all = sorted(
        int(x["Hash"] if isinstance(x, dict) else x)
        for x in gd.get("Bool64bitKey", [])
    )

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "collectibles.json"), "w", encoding="utf-8") as f:
        json.dump(collectibles_out, f, indent=2, ensure_ascii=False)
    hd_map_path = os.path.join(MAP_ASSETS_DIR, "maps", "hyrule_hd.webp")
    ow_map_image = "maps/hyrule_hd.webp" if os.path.isfile(hd_map_path) else es_content["map"]["image"]
    with open(os.path.join(OUT_DIR, "places.json"), "w", encoding="utf-8") as f:
        json.dump({
            "map": {
                "image": ow_map_image,
                "aspect": es_content["map"]["aspect"],
                "overworld_hyrule_tf": overworld_hf_tf,
            },
            "places": places_out,
        }, f, indent=2, ensure_ascii=False)
    with open(os.path.join(OUT_DIR, "categories.json"), "w", encoding="utf-8") as f:
        json.dump(categories_out, f, indent=2, ensure_ascii=False)
    with open(os.path.join(OUT_DIR, "requirements.json"), "w", encoding="utf-8") as f:
        json.dump(requirements_out, f, indent=2, ensure_ascii=False)
    with open(os.path.join(OUT_DIR, "ui_i18n.json"), "w", encoding="utf-8") as f:
        json.dump({
            "ui": i18n_core.UI_I18N,
            "regions": i18n_core.REGIONS_I18N,
            "floorLabels": i18n_core.FLOOR_LABELS_I18N,
            "locations": {
                loc_k: {
                    "zh-CN": loc_msgs["CNzh"].get(loc_k, loc_k),
                    "ja": loc_msgs["JPja"].get(loc_k, loc_k),
                    "en": loc_msgs["USen"].get(loc_k, loc_k),
                }
                for loc_k in loc_msgs["USen"]
            },
        }, f, indent=2, ensure_ascii=False)
    with open(os.path.join(OUT_DIR, "gamedata_hashes.json"), "w", encoding="utf-8") as f:
        json.dump({
            "hashes": hashes_map,
            "b64_known_sample": b64_all[:32],
            "b64_all_count": len(b64_all),
        }, f, indent=2, ensure_ascii=False)

    dbg_path = os.path.join(OUT_DIR, "_matched_debug.json")
    if os.path.exists(dbg_path):
        os.remove(dbg_path)
    print(f"Generated {len(collectibles_out)} collectibles, {len(places_out)} places, {len(categories_out)} categories, {len(hashes_map)} hashes successfully.")


if __name__ == "__main__":
    main()

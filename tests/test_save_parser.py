"""End-to-end verification tests for catalog, save parser, transforms, and FastAPI endpoints."""

from __future__ import annotations

import json
import math
import os
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from fastapi.testclient import TestClient  # noqa: E402
from backend.app import DATA_DIR, MAPS_DIR, app, catalog  # noqa: E402
from backend.live_sync import (  # noqa: E402
    LiveSyncService,
    TARGET_PROCESS_NAMES,
    WindowsProcessMemoryScanner,
    compute_yaw_deg_from_matrix,
)
from backend.save_parser import (  # noqa: E402
    discover_profiles_and_slots,
    extract_caption_thumbnail,
    parse_progress_sav,
)

DEFAULT_SAVE_ROOT = r"F:\games\SwitchGames\hookshot\game\user\save"


class TestOoTTracker(unittest.TestCase):
    def test_catalog_completeness(self):
        self.assertEqual(len(catalog.collectibles), 184)
        self.assertEqual(len(catalog.places), 32)
        self.assertEqual(len(catalog.categories), 7)

        for it in catalog.collectibles:
            self.assertIn("rule", it)
            self.assertIsNotNone(it["rule"], f"Missing rule on {it['id']}")
            for lang in ("zh-CN", "ja", "en"):
                self.assertTrue(it["title"][lang], f"Empty title {lang} on {it['id']}")
                self.assertTrue(it["guide"][lang], f"Empty guide {lang} on {it['id']}")

        # Verify all map assets exist on disk
        ow_img = os.path.join(MAPS_DIR, os.path.basename(catalog.overworld_map["image"]))
        self.assertTrue(os.path.isfile(ow_img), f"Missing overworld image: {ow_img}")
        for p in catalog.places:
            for m in p.get("maps", []):
                svg_path = os.path.join(MAPS_DIR, os.path.basename(m["image"]))
                self.assertTrue(os.path.isfile(svg_path), f"Missing map SVG: {svg_path}")
            for ex in p.get("exits", []):
                self.assertIn(ex["to"], catalog.places_by_id, f"Invalid exit target {ex['to']} on {p['id']}")
                self.assertTrue(0.0 <= ex["x"] <= 1.0 and 0.0 <= ex["y"] <= 1.0, f"OOB exit on {p['id']}: {ex}")
                if ex.get("icon"):
                    icon_path = os.path.join(MAPS_DIR, os.path.basename(ex["icon"]))
                    self.assertTrue(os.path.isfile(icon_path), f"Missing exit icon: {icon_path}")

        self.assertGreaterEqual(len(catalog.places_by_id["llanura"].get("exits", [])), 7)
        lw_exits = {ex["to"]: ex for ex in catalog.places_by_id["perdido"].get("exits", [])}
        self.assertEqual(set(lw_exits.keys()), {"prado", "goron", "rio", "kokiri"})
        # Verify Zora River exit is aligned with the blue pond (y ~= 0.418, not 0.388)
        self.assertAlmostEqual(lw_exits["rio"]["y"], 0.4182, places=3)
        # Verify Kakariko Bottom of the Well exit is on the well (x ~= 0.645, not 0.724 windmill)
        kak_pozo = next(ex for ex in catalog.places_by_id["kakariko"]["exits"] if ex["to"] == "pozo")
        self.assertAlmostEqual(kak_pozo["x"], 0.6450, places=3)
        self.assertAlmostEqual(kak_pozo["y"], 0.5125, places=3)
        # Verify Death Mountain Trail -> Goron City exit is on the tunnel mouth (not 0.630 trail)
        dmt_goron = next(ex for ex in catalog.places_by_id["sendero"]["exits"] if ex["to"] == "goron")
        self.assertAlmostEqual(dmt_goron["x"], 0.5328, places=3)
        self.assertAlmostEqual(dmt_goron["y"], 0.3202, places=3)
        # Verify Gerudo Fortress -> Gerudo Valley arrow points southwest (-144, not +144)
        gf_valle = next(ex for ex in catalog.places_by_id["fortaleza"]["exits"] if ex["to"] == "valle")
        self.assertEqual(gf_valle["rot"], -144)

    def test_magic_bean_rules_and_hashes(self):
        expected = {
            "kokiri-bean-01": ("IsPlantedMagicBean_SmallFarm.6092667454768667954", 3042626269),
            "perdido-bean-01": ("IsPlantedMagicBean_SmallFarm.5234955674857122897", 1589607563),
            "perdido-bean-02": ("IsPlantedMagicBean_SmallFarm.176409868210268833", 1628352828),
            "cementerio-bean-01": ("IsPlantedMagicBean_SmallFarm.17500344509500247365", 659258941),
            "sendero-bean-01": ("IsPlantedMagicBean_SmallFarm.18350441421271687772", 4073634450),
            "crater-bean-01": ("IsPlantedMagicBean_SmallFarm.12044463103654268862", 1445964662),
            "rio-bean-01": ("IsPlantedMagicBean_SmallFarm.17092212646454540992", 1592410278),
            "lago-bean-01": ("IsPlantedMagicBean_SmallFarm.6833516270248855649", 2956424759),
            "valle-bean-01": ("IsPlantedMagicBean_SmallFarm.10857724324414230743", 1352759134),
            "coloso-bean-01": ("IsPlantedMagicBean_SmallFarm.14429198438059673734", 706500814),
        }
        beans = {it["id"]: it for it in catalog.collectibles if it["cat"] == "bean"}
        self.assertEqual(set(beans.keys()), set(expected.keys()))
        try:
            import mmh3  # type: ignore
        except ImportError:
            mmh3 = None
        for bid, (flag, expected_hash) in expected.items():
            it = beans[bid]
            self.assertEqual(it["age"], "both", f"{bid} should be visible in both eras")
            self.assertEqual(it["rule"], {"type": "bool32", "flag": flag})
            self.assertEqual(catalog.hashes.get(flag), expected_hash)
            if mmh3 is not None:
                self.assertEqual(mmh3.hash(flag, 0, signed=False), expected_hash)

    def test_parse_synthetic_progress_sav_magic_beans(self):
        planted_ids = ["kokiri-bean-01", "rio-bean-01", "lago-bean-01"]
        unplanted_id = "crater-bean-01"
        beans_by_id = {it["id"]: it for it in catalog.collectibles if it["cat"] == "bean"}
        kv_pairs = [
            (catalog.hashes[beans_by_id[bid]["rule"]["flag"]], 1) for bid in planted_ids
        ] + [
            (catalog.hashes[beans_by_id[unplanted_id]["rule"]["flag"]], 0),
            # Pouring bugs (DiveInsectGameData) must NOT mark beans as planted
            (catalog.hashes.get("Gimmick_MagicBeanSoil_DeathMountainCrater", 2189915551), 1),
            (catalog.hashes.get("Gimmick_MagicBeanSoil_DesertColossus", 352515689), 1),
        ]
        end_off = 0x28 + len(kv_pairs) * 8
        buf = bytearray(end_off + 16)
        struct.pack_into("<III", buf, 0, 0x01020304, 0, end_off)
        for idx, (h, v) in enumerate(kv_pairs):
            struct.pack_into("<II", buf, 0x28 + idx * 8, h, v)

        with tempfile.TemporaryDirectory() as td:
            sav_path = os.path.join(td, "progress.sav")
            with open(sav_path, "wb") as f:
                f.write(buf)
            parsed = parse_progress_sav(sav_path, catalog)

        self.assertEqual(parsed["counts"]["by_cat"]["bean"], {"collected": 3, "total": 10})
        for bid in planted_ids:
            self.assertTrue(parsed["collected"][bid], f"{bid} should be collected")
        self.assertFalse(parsed["collected"][unplanted_id])
        self.assertFalse(parsed["collected"]["coloso-bean-01"])

    def test_chest_heart_piece_rules_and_synthetic_save(self):
        expected = {
            "llanura-heart-02": ("IsTreasureBoxOpen.2967378296224661060", 3667787564),
            "cementerio-heart-02": ("IsTreasureBoxOpen.5534919361313859554", 2201084167),
            "cementerio-heart-03": ("IsTreasureBoxOpen.9622128545943056087", 2626274661),
            "valle-heart-02": ("IsTreasureBoxOpen.15856256242099990922", 1879175548),
            "dominio-heart-01": ("IsTreasureBoxOpen.3130048366421939233", 2707918553),
            "fortaleza-heart-02": ("IsTreasureBoxOpen.12343753510713797715", 1755114472),
        }
        hearts = {it["id"]: it for it in catalog.collectibles if it["cat"] == "heart"}
        try:
            import mmh3  # type: ignore
        except ImportError:
            mmh3 = None
        for hid, (flag, expected_hash) in expected.items():
            self.assertEqual(hearts[hid]["rule"], {"type": "bool32", "flag": flag})
            self.assertEqual(catalog.hashes.get(flag), expected_hash)
            if mmh3 is not None:
                self.assertEqual(mmh3.hash(flag, 0, signed=False), expected_hash)

        opened_ids = ["dominio-heart-01", "valle-heart-02", "cementerio-heart-03"]
        kv_pairs = [(expected[hid][1], 1) for hid in opened_ids] + [
            (expected["fortaleza-heart-02"][1], 0),
        ]
        end_off = 0x28 + len(kv_pairs) * 8
        buf = bytearray(end_off + 16)
        struct.pack_into("<III", buf, 0, 0x01020304, 0, end_off)
        for idx, (h, v) in enumerate(kv_pairs):
            struct.pack_into("<II", buf, 0x28 + idx * 8, h, v)

        with tempfile.TemporaryDirectory() as td:
            sav_path = os.path.join(td, "progress.sav")
            with open(sav_path, "wb") as f:
                f.write(buf)
            parsed = parse_progress_sav(sav_path, catalog)

        self.assertEqual(parsed["counts"]["by_cat"]["heart"], {"collected": 3, "total": 36})
        for hid in opened_ids:
            self.assertTrue(parsed["collected"][hid], f"{hid} should be collected")
        self.assertFalse(parsed["collected"]["fortaleza-heart-02"])

    def test_parse_all_six_save_slots(self):
        if not os.path.isdir(DEFAULT_SAVE_ROOT):
            self.skipTest("Local save root not present")
        disc = discover_profiles_and_slots(DEFAULT_SAVE_ROOT, catalog)
        self.assertTrue(disc["exists"])
        all_slots = [s for p in disc["profiles"] for s in p["slots"]]
        self.assertEqual(len(all_slots), 6)

        for sl in all_slots:
            parsed = parse_progress_sav(sl["progress_path"], catalog)
            self.assertTrue(parsed["player"]["scene"])
            self.assertIsNotNone(parsed["player"]["pos"])
            self.assertIsNotNone(parsed["player"]["place"])
            self.assertIsNotNone(parsed["player"]["projected"]["overworld"])

            # Verify Skulltula count matches PouchData.Item_Token_Gold.StockNum (20)
            gs_done = sum(
                1
                for it in catalog.collectibles
                if it["cat"] == "gs" and parsed["collected"][it["id"]]
            )
            self.assertEqual(
                gs_done,
                parsed["summary"]["tokens"],
                f"Skulltula count mismatch in {sl['slot']}: {gs_done} vs {parsed['summary']['tokens']}",
            )

            # Verify caption.sav thumbnail extraction
            cap_path = os.path.join(sl["slot_dir"], "caption.sav")
            jpg = extract_caption_thumbnail(cap_path)
            self.assertIsNotNone(jpg)
            self.assertTrue(jpg.startswith(b"\xff\xd8\xff"))

    def test_fastapi_endpoints_and_websocket(self):
        with TestClient(app) as client:
            r = client.get("/")
            self.assertEqual(r.status_code, 200)
            self.assertIn("OoT Remake", r.text)

            cat_res = client.get("/api/catalog")
            self.assertEqual(cat_res.status_code, 200)
            cat_json = cat_res.json()
            self.assertEqual(len(cat_json["collectibles"]), 184)

            st_res = client.get("/api/state")
            self.assertEqual(st_res.status_code, 200)
            st_json = st_res.json()
            self.assertIn("sync", st_json)
            if os.path.isdir(DEFAULT_SAVE_ROOT):
                self.assertIsNotNone(st_json["save"])
                prof = st_json["config"]["profile"]
                slot = st_json["config"]["slot"]
                th = client.get(f"/api/saves/thumbnail?profile={prof}&slot={slot}")
                self.assertEqual(th.status_code, 200)
                self.assertEqual(th.headers["content-type"], "image/jpeg")

            bd = client.get("/api/browse-dir")
            self.assertEqual(bd.status_code, 200)
            self.assertIn("dirs", bd.json())

            with client.websocket_connect("/api/ws") as ws:
                msg = ws.receive_json()
                self.assertIn("sync", msg)
                self.assertIn("config", msg)

    def test_yaw_from_matrix_four_quadrants(self):
        for deg in (-180, -135, -90, -45, 0, 45, 90, 135, 180):
            rad = math.radians(deg)
            m_x = math.sin(rad)
            m_z = -math.cos(rad)
            yaw = compute_yaw_deg_from_matrix(m_x, m_z)
            self.assertIsNotNone(yaw)
            diff = (yaw - deg + 180.0) % 360.0 - 180.0
            self.assertLess(abs(diff), 0.02, f"Mismatch at {deg}: got {yaw}")

        self.assertIsNone(compute_yaw_deg_from_matrix(0.0, 0.0))
        self.assertIsNone(compute_yaw_deg_from_matrix(1e-5, -1e-5))
        self.assertIsNone(compute_yaw_deg_from_matrix(float("nan"), 1.0))
        self.assertIsNone(compute_yaw_deg_from_matrix(0.0, float("inf")))

    def test_target_process_names_include_longshot(self):
        self.assertIn("longshot.exe", TARGET_PROCESS_NAMES)

    def test_live_sync_player_only_change_kind(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "config.json"), "w", encoding="utf-8") as f:
                json.dump({"save_root": tmpdir, "auto_follow_slot": True, "language": "zh-CN"}, f)
            svc = LiveSyncService(tmpdir, catalog)

            mem_frames = [
                {
                    "process_running": True,
                    "process_name": "longshot.exe",
                    "live": {
                        "scene": "HyruleField_Child",
                        "is_child": True,
                        "pos": [10.0, 0.0, 20.0],
                        "rot": 45.0,
                    },
                },
                {
                    "process_running": True,
                    "process_name": "longshot.exe",
                    "live": {
                        "scene": "HyruleField_Child",
                        "is_child": True,
                        "pos": [10.002, 0.0, 20.002],
                        "rot": 45.02,
                    },
                },
                {
                    "process_running": True,
                    "process_name": "longshot.exe",
                    "live": {
                        "scene": "HyruleField_Child",
                        "is_child": True,
                        "pos": [15.5, 0.0, 22.3],
                        "rot": 90.0,
                    },
                },
                {
                    "process_running": False,
                    "process_name": None,
                    "live": None,
                },
            ]

            with patch.object(svc.scanner, "poll_live_state", side_effect=mem_frames):
                # 1st poll: mode transition idle -> live_memory => full
                self.assertTrue(svc.refresh_sync(force_rescan=True))
                self.assertEqual(svc._last_change_kind, "full")
                self.assertEqual(svc.sync_info["mode"], "live_memory")
                self.assertIsNotNone(svc.live_player)

                # 2nd poll: sub-deadzone jitter => no change
                self.assertFalse(svc.refresh_sync(force_rescan=False))
                self.assertEqual(svc._last_change_kind, "none")

                # 3rd poll: real movement in same mode => player-only incremental broadcast
                self.assertTrue(svc.refresh_sync(force_rescan=False))
                self.assertEqual(svc._last_change_kind, "player")
                self.assertEqual(svc.live_player["pos"], [15.5, 0.0, 22.3])

                # 4th poll: process exited => full state reset
                self.assertTrue(svc.refresh_sync(force_rescan=False))
                self.assertEqual(svc._last_change_kind, "full")
                self.assertEqual(svc.sync_info["mode"], "no_save")
                self.assertIsNone(svc.live_player)

    def test_longshot_scene_transition_reconciliation(self):
        sc = WindowsProcessMemoryScanner(catalog.hashes)

        # 1. Cold start with gui_valid=False falls back to fb_pos without locking _last_longshot_live
        s1 = sc._reconcile_longshot_sample(
            scene="HyruleField_Child",
            is_child=True,
            gui_available=True,
            gui_valid=False,
            gui_pos=None,
            gui_rot=None,
            fb_pos=[-10.0, 0.0, 20.0],
            fb_rot=15.0,
            now_mono=1.0,
        )
        self.assertEqual(s1, {"scene": "HyruleField_Child", "is_child": True, "pos": [-10.0, 0.0, 20.0], "rot": 15.0})
        self.assertIsNone(sc._last_longshot_live)

        # 2. Normal valid frame updates _last_longshot_live
        s2 = sc._reconcile_longshot_sample(
            scene="HyruleField_Child",
            is_child=True,
            gui_available=True,
            gui_valid=True,
            gui_pos=[-28.0, 0.0, -55.0],
            gui_rot=90.0,
            fb_pos=[-28.0, 0.0, -55.0],
            fb_rot=90.0,
            now_mono=2.0,
        )
        self.assertEqual(s2, {"scene": "HyruleField_Child", "is_child": True, "pos": [-28.0, 0.0, -55.0], "rot": 90.0})
        self.assertEqual(sc._last_longshot_live["scene"], "HyruleField_Child")

        # 3. Loading transition (gui_valid=False) holds last valid scene & pos despite stale fb_pos
        s3 = sc._reconcile_longshot_sample(
            scene="Market_Child",
            is_child=True,
            gui_available=True,
            gui_valid=False,
            gui_pos=None,
            gui_rot=None,
            fb_pos=[-28.0, 0.0, -55.0],
            fb_rot=90.0,
            now_mono=2.5,
        )
        self.assertEqual(s3, {"scene": "HyruleField_Child", "is_child": True, "pos": [-28.0, 0.0, -55.0], "rot": 90.0})

        # 4. Spawn completion immediately emits new scene & spawn pos
        s4 = sc._reconcile_longshot_sample(
            scene="Market_Child",
            is_child=True,
            gui_available=True,
            gui_valid=True,
            gui_pos=[0.0, 0.0, 58.0],
            gui_rot=180.0,
            fb_pos=[-28.0, 0.0, -55.0],
            fb_rot=90.0,
            now_mono=3.0,
        )
        self.assertEqual(s4, {"scene": "Market_Child", "is_child": True, "pos": [0.0, 0.0, 58.0], "rot": 180.0})

        # 5. Early scene flip while gui_valid=True & coords barely moved holds old scene up to 0.8s
        s5a = sc._reconcile_longshot_sample(
            scene="KakarikoVillage_Child",
            is_child=True,
            gui_available=True,
            gui_valid=True,
            gui_pos=[0.05, 0.0, 58.0],
            gui_rot=180.0,
            fb_pos=None,
            fb_rot=None,
            now_mono=10.0,
        )
        self.assertEqual(s5a["scene"], "Market_Child")
        self.assertEqual(s5a["pos"], [0.0, 0.0, 58.0])

        s5b = sc._reconcile_longshot_sample(
            scene="KakarikoVillage_Child",
            is_child=True,
            gui_available=True,
            gui_valid=True,
            gui_pos=[0.05, 0.0, 58.0],
            gui_rot=180.0,
            fb_pos=None,
            fb_rot=None,
            now_mono=10.4,
        )
        self.assertEqual(s5b["scene"], "Market_Child")

        # 5c: Once coords jump to new spawn, accepts new scene immediately
        s5c = sc._reconcile_longshot_sample(
            scene="KakarikoVillage_Child",
            is_child=True,
            gui_available=True,
            gui_valid=True,
            gui_pos=[-60.0, 0.0, 30.0],
            gui_rot=0.0,
            fb_pos=None,
            fb_rot=None,
            now_mono=10.5,
        )
        self.assertEqual(s5c, {"scene": "KakarikoVillage_Child", "is_child": True, "pos": [-60.0, 0.0, 30.0], "rot": 0.0})

        # 5d: Or if timeout >= 0.8s passes (e.g. two scenes actually spawn at the exact same coords)
        s5d_hold = sc._reconcile_longshot_sample(
            scene="Market_Child",
            is_child=True,
            gui_available=True,
            gui_valid=True,
            gui_pos=[-60.0, 0.0, 30.0],
            gui_rot=0.0,
            fb_pos=None,
            fb_rot=None,
            now_mono=11.0,
        )
        self.assertEqual(s5d_hold["scene"], "KakarikoVillage_Child")
        s5d_accept = sc._reconcile_longshot_sample(
            scene="Market_Child",
            is_child=True,
            gui_available=True,
            gui_valid=True,
            gui_pos=[-60.0, 0.0, 30.0],
            gui_rot=0.0,
            fb_pos=None,
            fb_rot=None,
            now_mono=11.85,
        )
        self.assertEqual(s5d_accept, {"scene": "Market_Child", "is_child": True, "pos": [-60.0, 0.0, 30.0], "rot": 0.0})


if __name__ == "__main__":
    unittest.main(verbosity=2)

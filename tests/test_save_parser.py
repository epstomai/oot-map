"""End-to-end verification tests for catalog, save parser, transforms, and FastAPI endpoints."""

from __future__ import annotations

import json
import math
import os
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

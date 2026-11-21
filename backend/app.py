"""FastAPI application for OoT Remake Local Collection Progress Manager & Live Sync."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import os
import string
from typing import Any

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .live_sync import DEFAULT_SAVE_ROOT, LiveSyncService
from .save_parser import CatalogStore, discover_profiles_and_slots, extract_caption_thumbnail

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
MAPS_DIR = os.path.join(DATA_DIR, "map_assets", "maps")

catalog = CatalogStore(DATA_DIR)
sync_service = LiveSyncService(DATA_DIR, catalog)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await sync_service.start()
    try:
        yield
    finally:
        await sync_service.stop()


app = FastAPI(title="OoT Collection & Live Tracker", lifespan=lifespan)


@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    if request.method == "OPTIONS":
        response = Response(status_code=204)
    else:
        response = await call_next(request)
    p = request.url.path
    if p == "/" or p.startswith("/static/") or p.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    elif p.startswith("/maps/"):
        response.headers["Cache-Control"] = "no-cache"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response


class SaveSelectReq(BaseModel):
    save_root: str | None = None
    profile: str | None = None
    slot: str | None = None
    auto_follow_slot: bool | None = None


class ManualCheckReq(BaseModel):
    item_id: str
    checked: bool | None = None
    note: str | None = None


class LanguageReq(BaseModel):
    language: str


@app.get("/")
async def index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/api/catalog")
async def get_catalog():
    return {
        "map": catalog.overworld_map,
        "places": catalog.places,
        "categories": catalog.categories,
        "requirements": catalog.requirements,
        "collectibles": catalog.collectibles,
        "i18n": catalog.ui_i18n,
    }


@app.get("/api/state")
async def get_state():
    return sync_service.get_state()


@app.get("/api/saves/scan")
async def scan_saves(path: str = Query(default=DEFAULT_SAVE_ROOT)):
    return discover_profiles_and_slots(path, catalog)


@app.post("/api/saves/select")
async def select_save(req: SaveSelectReq):
    state = sync_service.select_save(
        save_root=req.save_root,
        profile=req.profile,
        slot=req.slot,
        auto_follow_slot=req.auto_follow_slot,
    )
    await sync_service._broadcast()
    return state


@app.post("/api/language")
async def set_language(req: LanguageReq):
    sync_service.set_language(req.language)
    return {"language": sync_service.config["language"]}


@app.post("/api/manual-check")
async def set_manual_check(req: ManualCheckReq):
    overrides = sync_service.set_manual_override(req.item_id, req.checked, req.note)
    await sync_service._broadcast()
    return {"overrides": overrides}


@app.get("/api/saves/thumbnail")
async def get_slot_thumbnail(profile: str = Query(...), slot: str = Query(...)):
    for prof in sync_service.discovery.get("profiles", []):
        if prof["id"] == profile:
            for sl in prof.get("slots", []):
                if sl["slot"] == slot:
                    cap_path = os.path.join(sl["slot_dir"], "caption.sav")
                    jpg = extract_caption_thumbnail(cap_path)
                    if jpg:
                        return Response(content=jpg, media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="Thumbnail not found")


@app.get("/api/browse-dir")
async def browse_dir(path: str | None = Query(default=None)):
    if not path or not path.strip():
        target = sync_service.config.get("save_root") or DEFAULT_SAVE_ROOT
        if not os.path.isdir(target):
            target = os.path.expanduser("~")
    else:
        target = os.path.abspath(path.strip())

    # List Windows drives if requested
    drives = []
    if os.name == "nt":
        for ch in string.ascii_uppercase:
            dp = f"{ch}:\\"
            if os.path.isdir(dp):
                drives.append(dp)

    if not os.path.isdir(target):
        return JSONResponse(
            status_code=200,
            content={
                "path": target,
                "exists": False,
                "parent": os.path.dirname(target) if target else None,
                "drives": drives,
                "dirs": [],
                "has_progress_sav": False,
            },
        )

    parent = os.path.dirname(target.rstrip("\\/"))
    if parent == target or not parent:
        parent = None

    dirs = []
    try:
        for entry in sorted(os.scandir(target), key=lambda e: e.name.lower()):
            if entry.is_dir():
                has_sav = os.path.isfile(os.path.join(entry.path, "progress.sav"))
                has_slots = False
                if not has_sav:
                    try:
                        has_slots = any(
                            os.path.isfile(os.path.join(entry.path, sub, "progress.sav"))
                            for sub in os.listdir(entry.path)
                            if sub.startswith("slot_")
                        )
                    except OSError:
                        pass
                dirs.append(
                    {
                        "name": entry.name,
                        "path": entry.path,
                        "has_sav": has_sav,
                        "has_slots": has_slots,
                    }
                )
    except OSError:
        pass

    return {
        "path": target,
        "exists": True,
        "parent": parent,
        "drives": drives,
        "dirs": dirs,
        "has_progress_sav": os.path.isfile(os.path.join(target, "progress.sav")),
    }


@app.websocket("/api/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=16)

    async def listener(payload: dict[str, Any]) -> None:
        if queue.full():
            try:
                queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
        await queue.put(payload)

    sync_service.add_listener(listener)
    try:
        await ws.send_json(sync_service.get_state())
        while True:
            try:
                payload = await asyncio.wait_for(queue.get(), timeout=15.0)
                await ws.send_json(payload)
            except asyncio.TimeoutError:
                await ws.send_json({"ping": True})
    except WebSocketDisconnect:
        pass
    finally:
        sync_service.remove_listener(listener)


if os.path.isdir(MAPS_DIR):
    app.mount("/maps", StaticFiles(directory=MAPS_DIR), name="maps")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


def _is_port_available(host: str, port: int) -> bool:
    import socket

    # First check if anything is already accepting connections on loopback/host
    probe_host = "127.0.0.1" if host in ("0.0.0.0", "::", "") else host
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.05)
        if probe.connect_ex((probe_host, port)) == 0:
            return False

    # Then verify we can exclusively bind the port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def find_available_port(host: str, preferred_port: int, max_tries: int = 100) -> int:
    for offset in range(max_tries):
        candidate = preferred_port + offset
        if candidate > 65535:
            break
        if _is_port_available(host, candidate):
            return candidate
    raise RuntimeError(f"No available port found starting from {preferred_port}")


def main() -> None:
    import argparse
    import threading
    import webbrowser
    import uvicorn

    default_port = int(os.environ.get("OOT_MAP_PORT", "18765"))
    parser = argparse.ArgumentParser(description="OoT Collection & Live Tracker Server")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=default_port, help=f"Preferred port (default: {default_port})")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open the browser")
    args = parser.parse_args()

    port = find_available_port(args.host, args.port)
    if port != args.port:
        print(f"[OoT_Map] Port {args.port} is in use, switching to free port {port}.")
    url = f"http://{args.host}:{port}"
    print(f"[OoT_Map] Starting server at {url}")

    if not args.no_browser:
        threading.Timer(0.9, lambda: webbrowser.open(url)).start()

    uvicorn.run(app, host=args.host, port=port)


if __name__ == "__main__":
    main()


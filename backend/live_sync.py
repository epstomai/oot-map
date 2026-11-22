"""Real-time save file watcher and read-only Windows process memory live-sync."""

from __future__ import annotations

import array
import asyncio
import ctypes
from ctypes import wintypes
import json
import math
import os
import struct
import time
from typing import Any, Callable, Awaitable

from .save_parser import (
    CatalogStore,
    discover_profiles_and_slots,
    parse_progress_sav,
    project_player_positions,
    resolve_place_and_floor,
)

DEFAULT_SAVE_ROOT = r"F:\games\SwitchGames\hookshot\game\user\save"

TARGET_PROCESS_NAMES = {
    "longshot.exe",
    "hookshot.exe",
    "eden.exe",
    "citron.exe",
    "yuzu.exe",
    "ryujinx.exe",
    "suyu.exe",
    "sudachi.exe",
}

# Win32 constants for strictly read-only memory inspection
TH32CS_SNAPPROCESS = 0x00000002
PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
STILL_ACTIVE = 259
MEM_COMMIT = 0x1000
PAGE_GUARD = 0x100
PAGE_NOACCESS = 0x01
READABLE_PROTECT = {0x02, 0x04, 0x20, 0x40}  # R, RW, XR, XRW

# Longshot Switch 2 guest memory mapping & known OoT Remake (v1.1.0/v1.1.1) constants
DEFAULT_LONGSHOT_GUEST_BASE = 0x100000000000
GUEST_IMAGE_VA = 0x80000000
GUEST_MOD0_OFF = 0x301C
KNOWN_POS_STR_VA = 0x83D60DA6
KNOWN_GAMEDATA_GOT_VA = 0x84C9E180
KNOWN_GAMEUI_GOT_VA = 0x84C9E2A8
GAMEUI_VALID_OFF = 0x58A
GAMEUI_POS_OFF = 0x590
GAMEUI_ROT_PRIMARY_OFFS = (0x5F8, 0x610)
GAMEUI_ROT_BACKUP_OFFS = (0x5A4, 0x5BC)


def compute_yaw_deg_from_matrix(m_x: float, m_z: float) -> float | None:
    """Compute clockwise map bearing in degrees from GameUI rotation matrix components.

    0 deg = North/Up (-Z), +90 deg = East/Right (+X), +-180 deg = South/Down (+Z), -90 deg = West/Left (-X).
    Matches CSS clockwise `rotate(deg)` for an upward-pointing map arrow.
    Returns None if inputs are invalid or degenerate (near-zero vector).
    """
    if math.isnan(m_x) or math.isinf(m_x) or math.isnan(m_z) or math.isinf(m_z):
        return None
    if m_x * m_x + m_z * m_z <= 1e-6:
        return None
    deg = round(math.degrees(math.atan2(m_x, -m_z)), 2)
    return 0.0 if abs(deg) < 1e-6 else deg


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", wintypes.WCHAR * 260),
    ]


class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("PartitionId", wintypes.WORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]


def _find_adrp_add_xrefs(
    img: bytes, text_start: int, text_end: int, target_va: int, image_base: int = GUEST_IMAGE_VA
) -> list[int]:
    """Find ARM64 ADRP + ADD instructions referencing target_va in .text using stdlib array."""
    tpage = target_va & ~0xFFF
    tlo = target_va & 0xFFF
    insns = array.array("I")
    insns.frombytes(img[text_start:text_end])
    add_tag = 0x91000000 | (tlo << 10)
    results: list[int] = []
    for idx, insn in enumerate(insns):
        if (insn & 0xFFFFFC00) == add_tag:
            rn = (insn >> 5) & 0x1F
            for back in range(1, min(13, idx + 1)):
                ai = insns[idx - back]
                if (ai & 0x9F000000) == 0x90000000 and (ai & 0x1F) == rn:
                    immlo = (ai >> 29) & 0x3
                    immhi = (ai >> 5) & 0x7FFFF
                    imm = (immhi << 2) | immlo
                    if imm & (1 << 20):
                        imm -= 1 << 21
                    pc_va = image_base + text_start + (idx - back) * 4
                    page = (pc_va & ~0xFFF) + (imm << 12)
                    if page == tpage:
                        results.append(pc_va)
                    break
    return results


def _find_got_ldr_va(
    insns: array.array, text_start: int, pc_va: int, image_base: int = GUEST_IMAGE_VA
) -> list[int]:
    """Decode nearby ADRP + 64-bit LDR [Xn, #imm] instructions near pc_va to locate GOT entries."""
    center = (pc_va - image_base - text_start) // 4
    lo = max(0, center - 12)
    hi = min(len(insns), center + 16)
    gots: list[int] = []
    for i in range(lo, hi):
        ai = insns[i]
        if (ai & 0x9F000000) != 0x90000000:
            continue
        rd = ai & 0x1F
        immlo = (ai >> 29) & 0x3
        immhi = (ai >> 5) & 0x7FFFF
        imm = (immhi << 2) | immlo
        if imm & (1 << 20):
            imm -= 1 << 21
        adrp_pc = image_base + text_start + i * 4
        page = (adrp_pc & ~0xFFF) + (imm << 12)
        for d in range(1, min(11, len(insns) - i)):
            li = insns[i + d]
            if (li & 0xFFC00000) == 0xF9400000 and ((li >> 5) & 0x1F) == rd:
                got_va = page + (((li >> 10) & 0xFFF) << 3)
                if 0x84000000 <= got_va < 0x86000000 and got_va not in gots:
                    gots.append(got_va)
                break
    return gots


class WindowsProcessMemoryScanner:
    """Safely inspects running target process RAM (read-only) for live Hookshot/Longshot state."""

    def __init__(self, hashes: dict[str, int]):
        self.hashes = hashes
        self.h_banc = hashes["Sequence_CurrentBanc"]
        self.h_child = hashes["Sequence_IsChildhood"]
        self.h_pos = hashes["Player_Pos_For_Map"]
        self.h_rot = hashes["Player_Rot_For_Map"]

        self.attached_pid: int | None = None
        self.attached_name: str | None = None
        self.cached_base_addr: int | None = None
        self.cached_end_off: int = 0
        self.last_scan_ts: float = 0.0
        self.last_proc_enum_ts: float = 0.0
        self.longshot_guest_base: int | None = None
        self.longshot_gd_bss_va: int | None = None
        self.longshot_gui_bss_va: int | None = None
        self.cached_gd_inst: int | None = None
        self.cached_gd_entries: dict[str, int] = {}
        self._last_longshot_live: dict[str, Any] | None = None
        self._pending_scene_name: str | None = None
        self._pending_scene_since: float = 0.0

        self._k32 = ctypes.WinDLL("kernel32", use_last_error=True) if os.name == "nt" else None
        self._psapi = None
        if self._k32:
            self._k32.OpenProcess.restype = wintypes.HANDLE
            self._k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
            self._k32.CloseHandle.argtypes = [wintypes.HANDLE]
            self._k32.GetExitCodeProcess.restype = wintypes.BOOL
            self._k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
            self._k32.QueryFullProcessImageNameW.restype = wintypes.BOOL
            self._k32.QueryFullProcessImageNameW.argtypes = [
                wintypes.HANDLE,
                wintypes.DWORD,
                wintypes.LPWSTR,
                ctypes.POINTER(wintypes.DWORD),
            ]
            self._k32.ReadProcessMemory.restype = wintypes.BOOL
            self._k32.ReadProcessMemory.argtypes = [
                wintypes.HANDLE,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_size_t,
                ctypes.POINTER(ctypes.c_size_t),
            ]
            self._k32.VirtualQueryEx.restype = ctypes.c_size_t
            self._k32.VirtualQueryEx.argtypes = [
                wintypes.HANDLE,
                ctypes.c_void_p,
                ctypes.POINTER(MEMORY_BASIC_INFORMATION),
                ctypes.c_size_t,
            ]
            try:
                self._psapi = ctypes.WinDLL("psapi", use_last_error=True)
                self._psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
                self._psapi.GetProcessMemoryInfo.argtypes = [
                    wintypes.HANDLE,
                    ctypes.POINTER(PROCESS_MEMORY_COUNTERS),
                    wintypes.DWORD,
                ]
            except Exception:
                self._psapi = None

    def _reset_caches(self) -> None:
        self.cached_base_addr = None
        self.cached_end_off = 0
        self.last_scan_ts = 0.0
        self.longshot_guest_base = None
        self.longshot_gd_bss_va = None
        self.longshot_gui_bss_va = None
        self.cached_gd_inst = None
        self.cached_gd_entries = {}
        self._last_longshot_live = None
        self._pending_scene_name = None
        self._pending_scene_since = 0.0

    def _get_process_working_set(self, pid: int) -> int:
        if not self._k32 or not self._psapi:
            return 0
        handle = self._k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return 0
        try:
            pmc = PROCESS_MEMORY_COUNTERS()
            pmc.cb = ctypes.sizeof(pmc)
            if self._psapi.GetProcessMemoryInfo(handle, ctypes.byref(pmc), pmc.cb):
                return int(pmc.WorkingSetSize)
            return 0
        finally:
            self._k32.CloseHandle(handle)

    def find_target_processes(self) -> list[tuple[int, str]]:
        if not self._k32:
            return []
        snap = self._k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if snap == wintypes.HANDLE(-1).value:
            return []
        try:
            pe = PROCESSENTRY32W()
            pe.dwSize = ctypes.sizeof(PROCESSENTRY32W)
            ok = self._k32.Process32FirstW(snap, ctypes.byref(pe))
            matches: list[tuple[int, str, int, int]] = []
            while ok:
                exe = pe.szExeFile.lower()
                if exe in TARGET_PROCESS_NAMES:
                    pid = int(pe.th32ProcessID)
                    prio = 0 if exe == "longshot.exe" else (1 if exe == "hookshot.exe" else 2)
                    ws = self._get_process_working_set(pid)
                    matches.append((prio, pe.szExeFile, ws, pid))
                ok = self._k32.Process32NextW(snap, ctypes.byref(pe))
            matches.sort(key=lambda item: (item[0], -item[2], item[3]))
            return [(pid, name) for _prio, name, _ws, pid in matches]
        finally:
            self._k32.CloseHandle(snap)

    def find_target_process(self) -> tuple[int, str] | None:
        procs = self.find_target_processes()
        return procs[0] if procs else None

    def _read_bytes(self, handle: int, addr: int, size: int) -> bytes | None:
        buf = ctypes.create_string_buffer(size)
        read = ctypes.c_size_t(0)
        if self._k32.ReadProcessMemory(handle, ctypes.c_void_p(addr), buf, size, ctypes.byref(read)):
            return buf.raw[: read.value]
        return None

    def _read_u32(self, handle: int, addr: int) -> int | None:
        raw = self._read_bytes(handle, addr, 4)
        if raw and len(raw) == 4:
            return struct.unpack("<I", raw)[0]
        return None

    def _read_u64(self, handle: int, addr: int) -> int | None:
        raw = self._read_bytes(handle, addr, 8)
        if raw and len(raw) == 8:
            return struct.unpack("<Q", raw)[0]
        return None

    @staticmethod
    def _is_valid_guest_heap_ptr(ptr: int | None) -> bool:
        return ptr is not None and 0x100000000 <= ptr < 0x10000000000

    @staticmethod
    def _is_valid_guest_img_ptr(ptr: int | None) -> bool:
        return ptr is not None and 0x80000000 <= ptr < 0x90000000

    def _find_longshot_guest_base(self, handle: int) -> int | None:
        mbi = MEMORY_BASIC_INFORMATION()
        fast_img = DEFAULT_LONGSHOT_GUEST_BASE + GUEST_IMAGE_VA
        if self._k32.VirtualQueryEx(handle, ctypes.c_void_p(fast_img), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            if (
                mbi.State == MEM_COMMIT
                and (mbi.Protect & 0xFF) in READABLE_PROTECT
                and not (mbi.Protect & (PAGE_GUARD | PAGE_NOACCESS))
                and mbi.RegionSize >= 64 * 1024 * 1024
            ):
                if self._read_bytes(handle, fast_img + GUEST_MOD0_OFF, 4) == b"MOD0":
                    return DEFAULT_LONGSHOT_GUEST_BASE
                if self._read_bytes(handle, DEFAULT_LONGSHOT_GUEST_BASE + KNOWN_POS_STR_VA, 19) == b"Player_Pos_For_Map\x00":
                    return DEFAULT_LONGSHOT_GUEST_BASE

        addr = 0x10000
        max_addr = 0x7FFFFFFFFFFF
        while addr < max_addr:
            sz = self._k32.VirtualQueryEx(handle, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi))
            if sz == 0:
                break
            rsize = mbi.RegionSize
            if (
                mbi.State == MEM_COMMIT
                and (mbi.Protect & 0xFF) in READABLE_PROTECT
                and not (mbi.Protect & (PAGE_GUARD | PAGE_NOACCESS))
                and 64 * 1024 * 1024 <= rsize <= 256 * 1024 * 1024
            ):
                if (
                    self._read_bytes(handle, addr + GUEST_MOD0_OFF, 4) == b"MOD0"
                    and self._read_bytes(handle, addr, 4) == b"\x03\x00\x00\x14"
                ):
                    return addr - GUEST_IMAGE_VA
            addr += rsize
        return None

    def _resolve_longshot_singletons(self, handle: int, guest_base: int) -> tuple[int, int] | None:
        # Fast path for known Switch 2 OoT Remake v1.1.0/v1.1.1 offsets
        if self._read_bytes(handle, guest_base + KNOWN_POS_STR_VA, 19) == b"Player_Pos_For_Map\x00":
            gd_bss = self._read_u64(handle, guest_base + KNOWN_GAMEDATA_GOT_VA)
            gui_bss = self._read_u64(handle, guest_base + KNOWN_GAMEUI_GOT_VA)
            if (
                gd_bss is not None
                and gui_bss is not None
                and 0x84000000 <= gd_bss < 0x86000000
                and 0x84000000 <= gui_bss < 0x86000000
            ):
                return gd_bss, gui_bss

        # Dynamic fallback: scan guest image in 4 MB chunks without external deps
        mbi = MEMORY_BASIC_INFORMATION()
        img_host = guest_base + GUEST_IMAGE_VA
        read_limit = 96 * 1024 * 1024
        if self._k32.VirtualQueryEx(handle, ctypes.c_void_p(img_host), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            if mbi.RegionSize > 0:
                read_limit = min(128 * 1024 * 1024, int(mbi.RegionSize))

        chunks: list[bytes] = []
        chunk_sz = 4 * 1024 * 1024
        for off in range(0, read_limit, chunk_sz):
            part = self._read_bytes(handle, img_host + off, min(chunk_sz, read_limit - off))
            if not part:
                break
            chunks.append(part)
        if not chunks:
            return None
        img = b"".join(chunks)

        pos_idx = img.find(b"Player_Pos_For_Map\x00")
        if pos_idx == -1:
            return None
        pos_str_va = GUEST_IMAGE_VA + pos_idx

        rot_idx = img.find(b"Player_Rot_For_Map\x00")
        rot_str_va = (GUEST_IMAGE_VA + rot_idx) if rot_idx != -1 else None

        text_start = 0x10000
        text_end = min(len(img), 0x3D00000)
        if text_end <= text_start:
            return None

        xrefs = _find_adrp_add_xrefs(img, text_start, text_end, pos_str_va, GUEST_IMAGE_VA)
        if not xrefs:
            return None

        rot_xrefs = set(_find_adrp_add_xrefs(img, text_start, text_end, rot_str_va, GUEST_IMAGE_VA)) if rot_str_va else set()
        insns = array.array("I")
        insns.frombytes(img[text_start:text_end])

        gd_bss: int | None = None
        gui_bss: int | None = None
        for pc_va in xrefs:
            center = (pc_va - GUEST_IMAGE_VA - text_start) // 4
            win_hi = min(len(insns), center + 16)
            has_590 = any((insns[j] & 0xFFFFFC00) == (0x91000000 | (0x590 << 10)) for j in range(center, win_hi))
            gots = _find_got_ldr_va(insns, text_start, pc_va, GUEST_IMAGE_VA)
            if has_590 and gui_bss is None:
                for gva in gots:
                    val = self._read_u64(handle, guest_base + gva)
                    if val is not None and 0x84000000 <= val < 0x86000000:
                        inst = self._read_u64(handle, guest_base + val)
                        if self._is_valid_guest_heap_ptr(inst):
                            gui_bss = val
                            break
            elif not has_590 and gd_bss is None:
                has_rot = any(rx in range(pc_va, pc_va + 0x80) for rx in rot_xrefs) if rot_xrefs else True
                if has_rot:
                    for gva in gots:
                        val = self._read_u64(handle, guest_base + gva)
                        if val is not None and 0x84000000 <= val < 0x86000000:
                            inst = self._read_u64(handle, guest_base + val)
                            if self._is_valid_guest_heap_ptr(inst):
                                gd_bss = val
                                break
            if gd_bss is not None and gui_bss is not None:
                return gd_bss, gui_bss

        if gd_bss is not None and gui_bss is not None:
            return gd_bss, gui_bss
        return None

    def _lookup_gamedata_entry(
        self, handle: int, guest_base: int, gd_inst: int, sub_off: int, stride: int, target_hash: int
    ) -> int | None:
        hdr = self._read_bytes(handle, guest_base + gd_inst + sub_off, 0x30)
        if not hdr or len(hdr) < 0x30:
            return None
        count = struct.unpack_from("<I", hdr, 0x08)[0]
        arr_ptr = struct.unpack_from("<Q", hdr, 0x10)[0]
        ht_ptr = struct.unpack_from("<Q", hdr, 0x18)[0]
        ht_cap = struct.unpack_from("<I", hdr, 0x24)[0]
        if (
            count == 0
            or ht_cap == 0
            or ht_cap > 100000
            or not self._is_valid_guest_heap_ptr(arr_ptr)
            or not self._is_valid_guest_heap_ptr(ht_ptr)
        ):
            return None
        tbl = self._read_bytes(handle, guest_base + ht_ptr, ht_cap * 8)
        if not tbl or len(tbl) < ht_cap * 8:
            return None
        slot = target_hash % ht_cap
        for step in range(ht_cap):
            idx = (slot + step) % ht_cap
            hv, val_idx = struct.unpack_from("<II", tbl, idx * 8)
            if hv == target_hash:
                if val_idx < count:
                    return arr_ptr + val_idx * stride
                return None
            if hv == 0:
                return None
        return None

    def _reconcile_longshot_sample(
        self,
        *,
        scene: str,
        is_child: bool,
        gui_available: bool,
        gui_valid: bool,
        gui_pos: list[float] | None,
        gui_rot: float | None,
        fb_pos: list[float] | None,
        fb_rot: float | None,
        now_mono: float | None = None,
    ) -> dict[str, Any] | None:
        if gui_available and (not gui_valid or gui_pos is None):
            self._pending_scene_name = None
            self._pending_scene_since = 0.0
            if self._last_longshot_live is not None:
                held = dict(self._last_longshot_live)
                held["pos"] = list(held["pos"])
                return held
            if fb_pos is None:
                return None
            return {
                "scene": scene,
                "is_child": is_child,
                "pos": list(fb_pos),
                "rot": fb_rot if fb_rot is not None else 0.0,
            }

        if gui_available and gui_valid and gui_pos is not None:
            rot = gui_rot if gui_rot is not None else (fb_rot if fb_rot is not None else 0.0)
            if self._last_longshot_live is not None and scene != self._last_longshot_live["scene"]:
                dist = math.dist(gui_pos, self._last_longshot_live["pos"])
                if dist < 0.5:
                    now = time.monotonic() if now_mono is None else now_mono
                    if self._pending_scene_name != scene:
                        self._pending_scene_name = scene
                        self._pending_scene_since = now
                    if now - self._pending_scene_since < 0.8:
                        held = dict(self._last_longshot_live)
                        held["pos"] = list(held["pos"])
                        return held
                self._pending_scene_name = None
                self._pending_scene_since = 0.0
            else:
                self._pending_scene_name = None
                self._pending_scene_since = 0.0
            result = {
                "scene": scene,
                "is_child": is_child,
                "pos": list(gui_pos),
                "rot": rot,
            }
            saved = dict(result)
            saved["pos"] = list(result["pos"])
            self._last_longshot_live = saved
            return result

        self._pending_scene_name = None
        self._pending_scene_since = 0.0
        if fb_pos is None:
            return None
        return {
            "scene": scene,
            "is_child": is_child,
            "pos": list(fb_pos),
            "rot": fb_rot if fb_rot is not None else 0.0,
        }

    def _poll_longshot_live(self, handle: int, pname: str) -> dict[str, Any] | None:
        if self.longshot_guest_base is None or self.longshot_gd_bss_va is None:
            now = time.monotonic()
            if now - self.last_scan_ts < 3.0:
                return None
            self.last_scan_ts = now

            guest_base = self._find_longshot_guest_base(handle)
            if guest_base is None:
                return None
            resolved = self._resolve_longshot_singletons(handle, guest_base)
            if resolved is None:
                return None
            self.longshot_guest_base = guest_base
            self.longshot_gd_bss_va, self.longshot_gui_bss_va = resolved

        guest_base = self.longshot_guest_base
        gd_inst = self._read_u64(handle, guest_base + self.longshot_gd_bss_va)
        if not self._is_valid_guest_heap_ptr(gd_inst):
            self.cached_gd_inst = None
            self.cached_gd_entries = {}
            self._last_longshot_live = None
            self._pending_scene_name = None
            self._pending_scene_since = 0.0
            return None

        if gd_inst != self.cached_gd_inst or "banc" not in self.cached_gd_entries or "child" not in self.cached_gd_entries:
            if gd_inst != self.cached_gd_inst:
                self._last_longshot_live = None
                self._pending_scene_name = None
                self._pending_scene_since = 0.0
            entries: dict[str, int] = {}
            banc_e = self._lookup_gamedata_entry(handle, guest_base, gd_inst, 0x608, 0x108, self.h_banc)
            child_e = self._lookup_gamedata_entry(handle, guest_base, gd_inst, 0x008, 0x18, self.h_child)
            if banc_e is None or child_e is None:
                self.cached_gd_inst = None
                self.cached_gd_entries = {}
                self._last_longshot_live = None
                self._pending_scene_name = None
                self._pending_scene_since = 0.0
                return None
            entries["banc"] = banc_e
            entries["child"] = child_e
            pos_e = self._lookup_gamedata_entry(handle, guest_base, gd_inst, 0x3C8, 0x40, self.h_pos)
            rot_e = self._lookup_gamedata_entry(handle, guest_base, gd_inst, 0x188, 0x28, self.h_rot)
            if pos_e is not None:
                entries["pos"] = pos_e
            if rot_e is not None:
                entries["rot"] = rot_e
            self.cached_gd_inst = gd_inst
            self.cached_gd_entries = entries

        banc_entry = self.cached_gd_entries["banc"]
        child_entry = self.cached_gd_entries["child"]

        str_ptr = self._read_u64(handle, guest_base + banc_entry + 0x68)
        sraw = (
            self._read_bytes(handle, guest_base + str_ptr, 64)
            if self._is_valid_guest_heap_ptr(str_ptr)
            else self._read_bytes(handle, guest_base + banc_entry + 0x74, 64)
        )
        if not sraw:
            return None
        scene = sraw.split(b"\x00", 1)[0].decode("utf-8", errors="ignore")
        if not scene or not all(32 <= ord(ch) < 127 for ch in scene):
            return None

        child_raw = self._read_bytes(handle, guest_base + child_entry + 0x16, 1)
        if not child_raw:
            return None
        is_child = bool(child_raw[0])

        gui_available = False
        gui_valid = False
        gui_pos: list[float] | None = None
        gui_rot: float | None = None

        if self.longshot_gui_bss_va is not None:
            gui_inst = self._read_u64(handle, guest_base + self.longshot_gui_bss_va)
            if self._is_valid_guest_heap_ptr(gui_inst):
                blk = self._read_bytes(handle, guest_base + gui_inst + 0x588, 0x90)
                if blk and len(blk) >= 0x90:
                    gui_available = True
                    flags = struct.unpack_from("<H", blk, GAMEUI_VALID_OFF - 0x588)[0]
                    gui_valid = bool(flags & 1)
                    if gui_valid:
                        x, y, z = struct.unpack_from("<3f", blk, GAMEUI_POS_OFF - 0x588)
                        if all(not math.isnan(v) and not math.isinf(v) and abs(v) <= 50000 for v in (x, y, z)):
                            gui_pos = [round(x, 3), round(y, 3), round(z, 3)]
                            m_px = struct.unpack_from("<f", blk, GAMEUI_ROT_PRIMARY_OFFS[0] - 0x588)[0]
                            m_pz = struct.unpack_from("<f", blk, GAMEUI_ROT_PRIMARY_OFFS[1] - 0x588)[0]
                            gui_rot = compute_yaw_deg_from_matrix(m_px, m_pz)
                            if gui_rot is None:
                                m_bx = struct.unpack_from("<f", blk, GAMEUI_ROT_BACKUP_OFFS[0] - 0x588)[0]
                                m_bz = struct.unpack_from("<f", blk, GAMEUI_ROT_BACKUP_OFFS[1] - 0x588)[0]
                                gui_rot = compute_yaw_deg_from_matrix(m_bx, m_bz)

        fb_pos: list[float] | None = None
        if (not gui_available or (gui_pos is None and self._last_longshot_live is None)) and "pos" in self.cached_gd_entries:
            raw_pos = self._read_bytes(handle, guest_base + self.cached_gd_entries["pos"] + 0x24, 12)
            if raw_pos and len(raw_pos) == 12:
                x, y, z = struct.unpack("<3f", raw_pos)
                if all(not math.isnan(v) and not math.isinf(v) and abs(v) <= 50000 for v in (x, y, z)):
                    fb_pos = [round(x, 3), round(y, 3), round(z, 3)]

        fb_rot: float | None = None
        if gui_rot is None and (not gui_available or gui_valid or self._last_longshot_live is None) and "rot" in self.cached_gd_entries:
            raw_rot = self._read_bytes(handle, guest_base + self.cached_gd_entries["rot"] + 0x1C, 4)
            if raw_rot and len(raw_rot) == 4:
                rv = struct.unpack("<f", raw_rot)[0]
                if not math.isnan(rv) and not math.isinf(rv):
                    cw = round(-rv, 2)
                    fb_rot = 0.0 if abs(cw) < 1e-6 else cw

        return self._reconcile_longshot_sample(
            scene=scene,
            is_child=is_child,
            gui_available=gui_available,
            gui_valid=gui_valid,
            gui_pos=gui_pos,
            gui_rot=gui_rot,
            fb_pos=fb_pos,
            fb_rot=fb_rot,
        )

    def _parse_live_buffer(self, buf: bytes) -> dict[str, Any] | None:
        if len(buf) < 0x18000:
            return None
        magic, ver, end_off = struct.unpack("<3I", buf[:12])
        if magic != 0x01020304 or end_off < 0x17000 or end_off > len(buf):
            return None
        kv: dict[int, int] = {}
        for off in range(0x28, end_off, 8):
            h, v = struct.unpack("<II", buf[off : off + 8])
            kv[h] = v
        banc_off = kv.get(self.h_banc, 0)
        pos_off = kv.get(self.h_pos, 0)
        if not (end_off <= banc_off < len(buf) - 4) or not (end_off <= pos_off < len(buf) - 12):
            return None
        end = buf.find(b"\x00", banc_off, min(len(buf), banc_off + 96))
        if end == -1 or end == banc_off:
            return None
        scene = buf[banc_off:end].decode("utf-8", errors="ignore")
        if not scene or not all(32 <= ord(ch) < 127 for ch in scene):
            return None
        x, y, z = struct.unpack("<3f", buf[pos_off : pos_off + 12])
        if any(math.isnan(v) or math.isinf(v) or abs(v) > 50000 for v in (x, y, z)):
            return None
        rot_raw = kv.get(self.h_rot, 0)
        rot = struct.unpack("<f", struct.pack("<I", rot_raw))[0] if rot_raw else 0.0
        if math.isnan(rot) or math.isinf(rot):
            rot = 0.0
        else:
            rot = round(-rot, 2)
            if abs(rot) < 1e-6:
                rot = 0.0
        is_child = bool(kv.get(self.h_child, 1))
        return {
            "scene": scene,
            "is_child": is_child,
            "pos": [round(x, 3), round(y, 3), round(z, 3)],
            "rot": rot,
        }

    def _is_attached_handle_valid(self, handle: int, expected_name: str) -> bool:
        code = wintypes.DWORD(0)
        if not self._k32.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value != STILL_ACTIVE:
            return False
        buf = ctypes.create_unicode_buffer(260)
        sz = wintypes.DWORD(len(buf))
        if not self._k32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(sz)):
            return False
        return os.path.basename(buf.value).lower() == expected_name.lower()

    def poll_live_state(self) -> dict[str, Any]:
        if not self._k32:
            return {"process_running": False, "process_name": None, "live": None}

        handle = None
        pid: int | None = None
        pname: str | None = None

        # Fast path: reuse already attached PID without enumerating all OS processes
        now = time.monotonic()
        if self.attached_pid is not None and self.attached_name is not None:
            has_live_anchor = (
                self.longshot_guest_base is not None
                if self.attached_name.lower() == "longshot.exe"
                else self.cached_base_addr is not None
            )
            if has_live_anchor or (now - self.last_proc_enum_ts < 2.0):
                h = self._k32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, self.attached_pid)
                if h:
                    if self._is_attached_handle_valid(h, self.attached_name):
                        handle = h
                        pid = self.attached_pid
                        pname = self.attached_name
                    else:
                        self._k32.CloseHandle(h)

        if handle is None:
            self.last_proc_enum_ts = now
            candidates = self.find_target_processes()
            if not candidates:
                self.attached_pid = None
                self.attached_name = None
                self._reset_caches()
                return {"process_running": False, "process_name": None, "live": None}

            pid, pname = candidates[0]
            for cand_pid, cand_name in candidates:
                h = self._k32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, cand_pid)
                if h:
                    handle = h
                    pid = cand_pid
                    pname = cand_name
                    break

            if not handle:
                return {"process_running": True, "process_name": pname, "live": None}

            if pid != self.attached_pid:
                self.attached_pid = pid
                self.attached_name = pname
                self._reset_caches()

        try:
            if pname.lower() == "longshot.exe":
                live = self._poll_longshot_live(handle, pname)
                return {"process_running": True, "process_name": pname, "live": live}

            # Fast path: re-read cached save-buffer address
            if self.cached_base_addr is not None:
                raw = self._read_bytes(handle, self.cached_base_addr, 0x20000)
                if raw:
                    parsed = self._parse_live_buffer(raw)
                    if parsed:
                        return {"process_running": True, "process_name": pname, "live": parsed}
                self.cached_base_addr = None

            # Throttled region scan (at most once every 3 seconds)
            now = time.monotonic()
            if now - self.last_scan_ts < 3.0:
                return {"process_running": True, "process_name": pname, "live": None}
            self.last_scan_ts = now

            needle = struct.pack("<II", 0x01020304, 0x002D80EB)
            addr = 0x10000
            mbi = MEMORY_BASIC_INFORMATION()
            max_addr = 0x7FFFFFFFFFFF
            scanned = 0
            while addr < max_addr and scanned < 512 * 1024 * 1024:
                sz = self._k32.VirtualQueryEx(handle, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi))
                if sz == 0:
                    break
                rsize = mbi.RegionSize
                if (
                    mbi.State == MEM_COMMIT
                    and (mbi.Protect & 0xFF) in READABLE_PROTECT
                    and not (mbi.Protect & (PAGE_GUARD | PAGE_NOACCESS))
                    and 0x20000 <= rsize <= 64 * 1024 * 1024
                ):
                    raw = self._read_bytes(handle, addr, rsize)
                    if raw:
                        scanned += len(raw)
                        idx = raw.find(needle)
                        while idx != -1:
                            if idx + 0x20000 <= len(raw):
                                parsed = self._parse_live_buffer(raw[idx : idx + 0x20000])
                                if parsed:
                                    self.cached_base_addr = addr + idx
                                    return {"process_running": True, "process_name": pname, "live": parsed}
                            idx = raw.find(needle, idx + 8)
                addr += rsize
            return {"process_running": True, "process_name": pname, "live": None}
        finally:
            self._k32.CloseHandle(handle)


class LiveSyncService:
    def __init__(self, data_dir: str, catalog: CatalogStore):
        self.data_dir = data_dir
        self.catalog = catalog
        self.config_path = os.path.join(data_dir, "config.json")
        self.overrides_path = os.path.join(data_dir, "user_overrides.json")

        self.config = self._load_json(
            self.config_path,
            {
                "save_root": DEFAULT_SAVE_ROOT,
                "profile": None,
                "slot": None,
                "auto_follow_slot": True,
                "language": "zh-CN",
            },
        )
        self.overrides = self._load_json(self.overrides_path, {"checks": {}, "notes": {}})
        self.scanner = WindowsProcessMemoryScanner(catalog.hashes)

        self.discovery: dict[str, Any] = {"save_root": self.config["save_root"], "exists": False, "profiles": []}
        self.active_save: dict[str, Any] | None = None
        self.live_player: dict[str, Any] | None = None
        self._save_player_snapshot: dict[str, Any] | None = None
        self._last_disk_check_ts: float = 0.0
        self._last_change_kind: str = "none"
        self.last_sav_sig: tuple[str, int, int] | None = None
        self.last_mem_sig: tuple[Any, ...] | None = None
        self.sync_info: dict[str, Any] = {
            "mode": "idle",
            "process_running": False,
            "process_name": None,
            "memory_attached": False,
            "last_update_ts": time.time(),
        }
        self._listeners: set[Callable[[dict[str, Any]], Awaitable[None]]] = set()
        self._task: asyncio.Task | None = None

    @staticmethod
    def _load_json(path: str, default: dict[str, Any]) -> dict[str, Any]:
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    merged = dict(default)
                    merged.update(data)
                    return merged
            except Exception:
                pass
        return dict(default)

    def _save_json(self, path: str, data: dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_listener(self, cb: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
        self._listeners.add(cb)

    def remove_listener(self, cb: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
        self._listeners.discard(cb)

    async def _send_to_listeners(self, payload: dict[str, Any]) -> None:
        if not self._listeners:
            return
        dead = []
        for cb in list(self._listeners):
            try:
                await cb(payload)
            except Exception:
                dead.append(cb)
        for cb in dead:
            self._listeners.discard(cb)

    async def _broadcast(self) -> None:
        if not self._listeners:
            return
        await self._send_to_listeners(self.get_state())

    async def _broadcast_player(self) -> None:
        if not self._listeners:
            return
        await self._send_to_listeners(
            {
                "type": "player",
                "sync": self.sync_info,
                "player": self.live_player,
            }
        )

    def _find_best_slot(self, discovery: dict[str, Any]) -> dict[str, Any] | None:
        profiles = discovery.get("profiles", [])
        if not profiles:
            return None
        all_slots = [s for p in profiles for s in p.get("slots", [])]
        if not all_slots:
            return None

        if self.config.get("auto_follow_slot"):
            return max(all_slots, key=lambda s: s.get("mtime_ns", 0))

        prof_id = self.config.get("profile")
        slot_name = self.config.get("slot")
        for s in all_slots:
            if s["profile"] == prof_id and s["slot"] == slot_name:
                return s
        return max(all_slots, key=lambda s: s.get("mtime_ns", 0))

    def refresh_sync(self, force_rescan: bool = False) -> bool:
        full_changed = False
        player_changed = False

        now_mono = time.monotonic()
        should_check_disk = force_rescan or self.active_save is None or (now_mono - self._last_disk_check_ts >= 0.5)
        if should_check_disk:
            self._last_disk_check_ts = now_mono
            save_root = self.config.get("save_root") or DEFAULT_SAVE_ROOT
            if force_rescan or not self.discovery.get("profiles"):
                self.discovery = discover_profiles_and_slots(save_root, self.catalog)
            else:
                # Lightweight check for newest mtime across slots
                for prof in self.discovery.get("profiles", []):
                    for slot in prof.get("slots", []):
                        p = slot["progress_path"]
                        if os.path.isfile(p):
                            st = os.stat(p)
                            if st.st_mtime_ns != slot.get("mtime_ns"):
                                self.discovery = discover_profiles_and_slots(save_root, self.catalog)
                                break
                    else:
                        continue
                    break

            chosen = self._find_best_slot(self.discovery)
            if chosen:
                self.config["profile"] = chosen["profile"]
                self.config["slot"] = chosen["slot"]
                sav_path = chosen["progress_path"]
                try:
                    st = os.stat(sav_path)
                    sig = (sav_path, st.st_mtime_ns, st.st_size)
                    if force_rescan or sig != self.last_sav_sig or self.active_save is None:
                        for attempt in range(3):
                            try:
                                self.active_save = parse_progress_sav(sav_path, self.catalog)
                                self._save_player_snapshot = dict(self.active_save["player"])
                                self.last_sav_sig = sig
                                full_changed = True
                                break
                            except Exception:
                                if attempt == 2:
                                    raise
                                time.sleep(0.05)
                except Exception:
                    pass
            else:
                if self.active_save is not None:
                    self.active_save = None
                    self._save_player_snapshot = None
                    self.last_sav_sig = None
                    full_changed = True

        # Check live process memory
        mem = self.scanner.poll_live_state()
        live = mem.get("live")
        if live:
            place_id, floor_id = resolve_place_and_floor(
                live["scene"], live["pos"], live["is_child"], self.catalog
            )
            projected = project_player_positions(
                live["scene"], place_id, floor_id, live["pos"], self.catalog
            )
            player_payload = {
                "scene": live["scene"],
                "place": place_id,
                "floor": floor_id,
                "age": "child" if live["is_child"] else "adult",
                "pos": live["pos"],
                "rot": live["rot"],
                "projected": projected,
            }
            self.live_player = player_payload
            if self.active_save:
                self.active_save["player"] = player_payload
            mem_sig = (
                live["scene"],
                live["is_child"],
                round(live["pos"][0], 2),
                round(live["pos"][1], 2),
                round(live["pos"][2], 2),
                round(live["rot"], 1),
            )
            if mem_sig != self.last_mem_sig:
                self.last_mem_sig = mem_sig
                player_changed = True
            new_mode = "live_memory"
        else:
            if self.live_player is not None:
                self.live_player = None
                if self.active_save and self._save_player_snapshot is not None:
                    self.active_save["player"] = dict(self._save_player_snapshot)
                full_changed = True
            self.last_mem_sig = None
            new_mode = "save_watch" if self.active_save else "no_save"

        if (
            new_mode != self.sync_info["mode"]
            or mem["process_running"] != self.sync_info["process_running"]
            or mem["process_name"] != self.sync_info["process_name"]
            or bool(live) != self.sync_info["memory_attached"]
        ):
            full_changed = True

        self.sync_info = {
            "mode": new_mode,
            "process_running": mem["process_running"],
            "process_name": mem["process_name"],
            "memory_attached": bool(live),
            "last_update_ts": time.time(),
        }
        self._last_change_kind = "full" if full_changed else ("player" if player_changed else "none")
        return self._last_change_kind != "none"

    def select_save(
        self,
        save_root: str | None = None,
        profile: str | None = None,
        slot: str | None = None,
        auto_follow_slot: bool | None = None,
    ) -> dict[str, Any]:
        if save_root is not None:
            self.config["save_root"] = save_root.strip()
        if profile is not None:
            self.config["profile"] = profile
        if slot is not None:
            self.config["slot"] = slot
        if auto_follow_slot is not None:
            self.config["auto_follow_slot"] = bool(auto_follow_slot)
        self._save_json(self.config_path, self.config)
        self.last_sav_sig = None
        self.refresh_sync(force_rescan=True)
        return self.get_state()

    def set_language(self, lang: str) -> None:
        if lang in ("zh-CN", "ja", "en"):
            self.config["language"] = lang
            self._save_json(self.config_path, self.config)

    def set_manual_override(self, item_id: str, checked: bool | None = None, note: str | None = None) -> dict[str, Any]:
        if checked is None:
            self.overrides["checks"].pop(item_id, None)
        else:
            self.overrides["checks"][item_id] = bool(checked)
        if note is not None:
            if note.strip():
                self.overrides["notes"][item_id] = note
            else:
                self.overrides["notes"].pop(item_id, None)
        self._save_json(self.overrides_path, self.overrides)
        return self.overrides

    def get_state(self) -> dict[str, Any]:
        return {
            "config": self.config,
            "sync": self.sync_info,
            "discovery": self.discovery,
            "save": self.active_save,
            "live_player": self.live_player,
            "overrides": self.overrides,
        }

    async def start(self) -> None:
        self.refresh_sync(force_rescan=True)
        if self._task is None:
            self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _loop(self) -> None:
        while True:
            try:
                changed = await asyncio.to_thread(self.refresh_sync, False)
                if changed:
                    if self._last_change_kind == "player":
                        await self._broadcast_player()
                    else:
                        await self._broadcast()
            except asyncio.CancelledError:
                raise
            except Exception:
                pass
            await asyncio.sleep(0.10 if self.sync_info.get("memory_attached") else 0.35)

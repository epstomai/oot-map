"""Pure-Python reader for Switch 2 OoT Remake (Hookshot) ROMFS files:
- ZsDic.pack.zs dictionary loader
- SARC archive parser
- BYML v7 (BE/LE) parser
- MSBT (UTF-8 / UTF-16) parser with 0x0E/0x0F control-tag skipping
"""

from __future__ import annotations

import os
import struct
from typing import Any

import zstandard


def parse_sarc(data: bytes) -> dict[str, bytes]:
    if data[:4] != b"SARC":
        raise ValueError(f"Not a SARC archive: {data[:4]!r}")
    bom = "<" if data[6:8] == b"\xff\xfe" else ">"
    data_offset = struct.unpack(bom + "I", data[12:16])[0]
    if data[20:24] != b"SFAT":
        raise ValueError("Missing SFAT header")
    count = struct.unpack(bom + "H", data[26:28])[0]
    sfat_end = 20 + 12 + count * 16
    if data[sfat_end : sfat_end + 4] != b"SFNT":
        raise ValueError("Missing SFNT header")
    sfnt_off = sfat_end + 8
    files: dict[str, bytes] = {}
    for i in range(count):
        off = 32 + i * 16
        _h, flags, start, end = struct.unpack(bom + "4I", data[off : off + 16])
        noff = (flags & 0xFFFF) * 4 + sfnt_off
        nend = data.index(b"\x00", noff)
        name = data[noff:nend].decode("utf-8")
        files[name] = data[data_offset + start : data_offset + end]
    return files


def parse_byml(data: bytes) -> Any:
    magic = data[:2]
    if magic not in (b"BY", b"YB"):
        raise ValueError(f"Not a BYML file: {magic!r}")
    bom = ">" if magic == b"BY" else "<"
    endian = "big" if bom == ">" else "little"
    ht_off, st_off, root_off = struct.unpack(bom + "III", data[4:16])

    def read_str_table(off: int) -> list[str]:
        if off == 0:
            return []
        if data[off] != 0xC2:
            raise ValueError(f"Expected string table 0xC2 at 0x{off:x}, got 0x{data[off]:x}")
        cnt = int.from_bytes(data[off + 1 : off + 4], endian)
        offs = [struct.unpack(bom + "I", data[off + 4 + i * 4 : off + 8 + i * 4])[0] for i in range(cnt + 1)]
        return [data[off + offs[i] : off + offs[i + 1] - 1].decode("utf-8", errors="replace") for i in range(cnt)]

    keys = read_str_table(ht_off)
    strs = read_str_table(st_off)

    def read_u24(pos: int) -> int:
        return int.from_bytes(data[pos : pos + 3], endian)

    def read_node(ntype: int, val_bytes: bytes) -> Any:
        if ntype == 0xA0:
            return strs[struct.unpack(bom + "I", val_bytes)[0]]
        if ntype == 0xA1:
            off = struct.unpack(bom + "I", val_bytes)[0]
            sz = struct.unpack(bom + "I", data[off : off + 4])[0]
            return data[off + 4 : off + 4 + sz]
        if ntype == 0xC0:
            off = struct.unpack(bom + "I", val_bytes)[0]
            cnt = read_u24(off + 1)
            types = data[off + 4 : off + 4 + cnt]
            vals_off = (off + 4 + cnt + 3) & ~3
            return [read_node(types[i], data[vals_off + i * 4 : vals_off + i * 4 + 4]) for i in range(cnt)]
        if ntype == 0xC1:
            off = struct.unpack(bom + "I", val_bytes)[0]
            cnt = read_u24(off + 1)
            res: dict[str, Any] = {}
            pos = off + 4
            for _ in range(cnt):
                kidx = read_u24(pos)
                nt = data[pos + 3]
                res[keys[kidx]] = read_node(nt, data[pos + 4 : pos + 8])
                pos += 8
            return res
        if ntype == 0xD0:
            return struct.unpack(bom + "I", val_bytes)[0] != 0
        if ntype == 0xD1:
            return struct.unpack(bom + "i", val_bytes)[0]
        if ntype == 0xD2:
            return struct.unpack(bom + "f", val_bytes)[0]
        if ntype == 0xD3:
            return struct.unpack(bom + "I", val_bytes)[0]
        if ntype == 0xD4:
            off = struct.unpack(bom + "I", val_bytes)[0]
            return struct.unpack(bom + "q", data[off : off + 8])[0]
        if ntype == 0xD5:
            off = struct.unpack(bom + "I", val_bytes)[0]
            return struct.unpack(bom + "Q", data[off : off + 8])[0]
        if ntype == 0xD6:
            off = struct.unpack(bom + "I", val_bytes)[0]
            return struct.unpack(bom + "d", data[off : off + 8])[0]
        if ntype == 0x00:
            return None
        return None

    if root_off == 0:
        return None
    return read_node(data[root_off], struct.pack(bom + "I", root_off))


def decode_msbt_text(raw: bytes, encoding: int, bom: str) -> str:
    out: list[str] = []
    if encoding == 0:  # UTF-8
        i = 0
        n = len(raw)
        while i < n:
            b = raw[i]
            if b == 0:
                break
            if b == 0x0E:
                if i + 7 <= n:
                    plen = struct.unpack(bom + "H", raw[i + 5 : i + 7])[0]
                    i += 7 + plen
                else:
                    break
            elif b == 0x0F:
                if i + 5 <= n:
                    i += 5
                else:
                    break
            elif b < 0x80:
                out.append(chr(b))
                i += 1
            elif (b & 0xE0) == 0xC0:
                out.append(raw[i : i + 2].decode("utf-8", errors="replace"))
                i += 2
            elif (b & 0xF0) == 0xE0:
                out.append(raw[i : i + 3].decode("utf-8", errors="replace"))
                i += 3
            elif (b & 0xF8) == 0xF0:
                out.append(raw[i : i + 4].decode("utf-8", errors="replace"))
                i += 4
            else:
                i += 1
        return "".join(out)
    else:  # UTF-16
        i = 0
        n = len(raw) - 1
        while i < n:
            u = struct.unpack(bom + "H", raw[i : i + 2])[0]
            if u == 0:
                break
            if u == 0x0E:
                if i + 8 <= len(raw):
                    plen = struct.unpack(bom + "H", raw[i + 6 : i + 8])[0]
                    i += 8 + plen
                else:
                    break
            elif u == 0x0F:
                i += 6
            else:
                out.append(chr(u))
                i += 2
        return "".join(out)


def parse_msbt(data: bytes) -> dict[str, str]:
    if data[:8] != b"MsgStdBn":
        raise ValueError("Not an MSBT file")
    bom = "<" if data[8:10] == b"\xff\xfe" else ">"
    encoding = data[12]
    sec_count = struct.unpack(bom + "H", data[14:16])[0]
    pos = 0x20
    labels: dict[int, str] = {}
    texts: list[str] = []
    for _ in range(sec_count):
        tag = data[pos : pos + 4]
        sz = struct.unpack(bom + "I", data[pos + 4 : pos + 8])[0]
        sec = data[pos + 16 : pos + 16 + sz]
        if tag == b"LBL1":
            cnt = struct.unpack(bom + "I", sec[:4])[0]
            for i in range(cnt):
                lcnt, loff = struct.unpack(bom + "II", sec[4 + i * 8 : 12 + i * 8])
                p = loff
                for _ in range(lcnt):
                    slen = sec[p]
                    name = sec[p + 1 : p + 1 + slen].decode("utf-8")
                    idx = struct.unpack(bom + "I", sec[p + 1 + slen : p + 5 + slen])[0]
                    labels[idx] = name
                    p += 5 + slen
        elif tag == b"TXT2":
            cnt = struct.unpack(bom + "I", sec[:4])[0]
            offs = [struct.unpack(bom + "I", sec[4 + i * 4 : 8 + i * 4])[0] for i in range(cnt)] + [len(sec)]
            for i in range(cnt):
                texts.append(decode_msbt_text(sec[offs[i] : offs[i + 1]], encoding, bom))
        pos += 16 + ((sz + 15) & ~15)
    return {labels.get(i, str(i)): texts[i] for i in range(len(texts))}


class RomfsReader:
    def __init__(self, romfs_dir: str):
        self.romfs_dir = romfs_dir
        with open(os.path.join(romfs_dir, "Pack", "ZsDic.pack.zs"), "rb") as f:
            raw = zstandard.ZstdDecompressor().decompress(f.read())
        dics = parse_sarc(raw)
        self.dics = {
            k: zstandard.ZstdDecompressor(dict_data=zstandard.ZstdCompressionDict(v))
            for k, v in dics.items()
        }
        self.zs = self.dics["zs.zsdic"]
        self.bcett = self.dics["bcett.byml.zsdic"]

    def read_byml_zs(self, rel_path: str, use_bcett: bool = False) -> Any:
        path = os.path.join(self.romfs_dir, rel_path)
        with open(path, "rb") as f:
            raw = f.read()
        dec = (self.bcett if use_bcett else self.zs).decompress(raw)
        return parse_byml(dec)

    def read_byml(self, rel_path: str) -> Any:
        path = os.path.join(self.romfs_dir, rel_path)
        with open(path, "rb") as f:
            return parse_byml(f.read())

    def read_sarc_zs(self, rel_path: str) -> dict[str, bytes]:
        path = os.path.join(self.romfs_dir, rel_path)
        with open(path, "rb") as f:
            return parse_sarc(self.zs.decompress(f.read()))

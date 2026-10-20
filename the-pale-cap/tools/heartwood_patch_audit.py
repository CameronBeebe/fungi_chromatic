"""Decode the Heartwood harness's existing Hi-Color bytes; never rebuild assets.

This is deliberately format-specific: unsigned tile addressing, 20x18 cells,
and png2hicolorgb's alternating palette schedule. Not a general ROM decoder.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import struct

from PIL import Image

FOOTPRINT = (104, 80, 32, 24)  # XYWH, authored resource site, not a Jev box.


def sha(data):
    return hashlib.sha256(data).hexdigest()


def c_array(text, name, bits):
    matches = re.findall(
        r"const uint" + str(bits) + r"_t\s+" + re.escape(name) + r"\[\]\s*=\s*\{([^}]*)\};", text
    )
    if len(matches) != 1:
        raise ValueError("Missing/duplicate array: " + name)
    parts = [p.strip() for p in matches[0].split(",")]
    if parts and parts[-1] == "":
        parts.pop()
    if not parts or any(not re.fullmatch(r"\d+", p) for p in parts):
        raise ValueError("Expected literal unsigned array: " + name)
    values = [int(p) for p in parts]
    if any(v >= 2**bits for v in values):
        raise ValueError("Array value out of range")
    return values


def pattern_ids(tilemap, attrs):
    if len(tilemap) != 360 or len(attrs) != 360:
        raise ValueError("Expected 20x18 map and attributes")
    return [tilemap[i] + (256 if attrs[i] & 8 else 0) for i in range(360)]


def decode(tiles, tilemap, attrs, palettes):
    ids = pattern_ids(tilemap, attrs)
    if len(tiles) % 16 or len(tiles) // 16 <= max(ids) or len(palettes) != 4640:
        raise ValueError("Invalid Heartwood tile/palette data sizes")
    result = Image.new("RGB", (160, 144))
    pixels = result.load()
    for y in range(144):
        for x in range(160):
            cell = (y // 8) * 20 + x // 8
            attr = attrs[cell]
            tx, ty = x % 8, y % 8
            if attr & 0x20:
                tx = 7 - tx
            if attr & 0x40:
                ty = 7 - ty
            offset = ids[cell] * 16 + ty * 2
            index = ((tiles[offset] >> (7 - tx)) & 1) | (((tiles[offset + 1] >> (7 - tx)) & 1) << 1)
            slot = attr & 7
            block = ((y + 1) // 2) * 64 if slot < 4 else (y // 2) * 64 + 32
            value = struct.unpack_from("<H", palettes, block + (slot % 4) * 8 + index * 2)[0]
            pixels[x, y] = tuple(((value >> shift) & 31) * 255 // 31 for shift in (0, 5, 10))
    return result


def apply_patch(tiles, tilemap, attrs, ids, full, cut, footprint=FOOTPRINT):
    if not ids or len(set(ids)) != len(ids) or len(full) != len(ids) * 16 or len(cut) != len(full):
        raise ValueError("Invalid patch size or duplicate pattern IDs")
    x, y, w, h = footprint
    if (
        min(x, y) < 0
        or w <= 0
        or h <= 0
        or x + w > 160
        or y + h > 144
        or any(v % 8 for v in footprint)
    ):
        raise ValueError("Patch must fit a tile-aligned native rectangle")
    expected = {
        row * 20 + col for row in range(y // 8, (y + h) // 8) for col in range(x // 8, (x + w) // 8)
    }
    mapped = pattern_ids(tilemap, attrs)
    actual = {cell for cell, identity in enumerate(mapped) if identity in ids}
    if actual != expected or len(ids) != len(expected):
        raise ValueError("Patch IDs alias, miss or escape the authored footprint")
    output = bytearray(tiles)
    for i, identity in enumerate(ids):
        start = identity * 16
        if start + 16 > len(tiles) or tiles[start : start + 16] != full[i * 16 : (i + 1) * 16]:
            raise ValueError("Full patch does not match master bytes")
        output[start : start + 16] = cut[i * 16 : (i + 1) * 16]
    return bytes(output)


def audit_pixels(before, after, footprint=FOOTPRINT):
    if before.size != (160, 144) or after.size != before.size:
        raise ValueError("Expected matching 160x144 native frames")
    x, y, w, h = footprint
    if min(x, y) < 0 or w <= 0 or h <= 0 or x + w > 160 or y + h > 144:
        raise ValueError("Invalid edit footprint")
    before, after = before.convert("RGB"), after.convert("RGB")
    changed = []
    outside = 0
    diff = Image.new("RGB", before.size, (9, 16, 25))
    for py in range(144):
        for px in range(160):
            if before.getpixel((px, py)) != after.getpixel((px, py)):
                changed.append((px, py))
                escaped = not (x <= px < x + w and y <= py < y + h)
                outside += int(escaped)
                diff.putpixel((px, py), (255, 65, 95) if escaped else (56, 231, 224))
    bbox = (
        None
        if not changed
        else [
            min(p[0] for p in changed),
            min(p[1] for p in changed),
            max(p[0] for p in changed) + 1,
            max(p[1] for p in changed) + 1,
        ]
    )
    return {
        "changedPixels": len(changed),
        "outsidePixels": outside,
        "changedBoundsXYXY": bbox,
        "footprintXYWH": list(footprint),
        "localityPassed": outside == 0,
        "nonemptyChangePassed": bool(changed),
        "passed": outside == 0 and bool(changed),
    }, diff


def load_patch(folder):
    folder = Path(folder)
    raw = {
        suffix: (folder / ("master." + suffix)).read_bytes()
        for suffix in ("til", "map", "atr", "pal")
    }
    text = (folder / "assets.h").read_text()
    ids = c_array(text, "resource_ids", 16)
    full, cut = (bytes(c_array(text, name, 8)) for name in ("resource_full", "resource_cut"))
    patched = apply_patch(raw["til"], raw["map"], raw["atr"], ids, full, cut)
    before = decode(raw["til"], raw["map"], raw["atr"], raw["pal"])
    after = decode(patched, raw["map"], raw["atr"], raw["pal"])
    report, diff = audit_pixels(before, after)
    report.update(
        {
            "patchBytes": len(cut),
            "patchPatterns": len(ids),
            "patternIds": ids,
            "paletteScheduleUnchanged": True,
            "mapAndAttributesUnchanged": True,
            "sourceHashes": {key: sha(value) for key, value in raw.items()},
            "patchSHA256": sha(cut),
            "afterTilesSHA256": sha(patched),
            "scope": "Existing Heartwood encoded harvest patch. No ROM timing or gameplay certification.",
        }
    )
    return before, after, diff, report

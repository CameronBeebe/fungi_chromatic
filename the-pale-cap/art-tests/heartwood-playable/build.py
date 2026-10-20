"""Native-cell experiment: one Hi-Color master, fixed palettes, local tile updates.

Uses preserved local concept input, never edits or distributes that input.
Requires Pillow and the existing GBDK toolchain. All generated output is ignored.
"""

from pathlib import Path
import argparse
import hashlib
import json
import os
import struct
import subprocess
from collections import deque
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
parser = argparse.ArgumentParser()
parser.add_argument(
    "--source",
    type=Path,
    default=PROJECT.parent
    / "concept-art/heartwood-assets-candidate-v1/source/layout-reference-160x144.png",
)
parser.add_argument("--gbdk", type=Path, default=os.environ.get("GBDK_PATH"))
args = parser.parse_args()
if args.gbdk is None:
    parser.error("Set GBDK_PATH to a GBDK-2020 installation, or pass --gbdk.")
if not (args.gbdk / "bin/lcc").is_file() or not (args.gbdk / "bin/png2hicolorgb").is_file():
    parser.error("GBDK_PATH/--gbdk must contain bin/lcc and bin/png2hicolorgb.")
if not args.source.is_file():
    parser.error(
        "This local study requires concept-art/ input. Supply an original 160x144 PNG with --source; see the study README."
    )

out = ROOT / "build"
out.mkdir(exist_ok=True)
base = Image.open(args.source).convert("RGB")
assert base.size == (160, 144)

# New native-cell resource study; source painting is unchanged. Three asymmetric
# ochre fans, a shaded attachment and scattered cut remains, all in one footprint.
full = base.copy()
d = ImageDraw.Draw(full)
for x, y, r in [(109, 86, 5), (123, 89, 6), (116, 96, 4)]:
    d.line((x - 3, y + 4, x + 4, y + 4), fill=(51, 40, 46), width=2)
    d.line((x, y, x, y + 4), fill=(148, 103, 63))
    d.polygon(
        [
            (x - r, y),
            (x - r + 2, y - 3),
            (x + 1, y - 4),
            (x + r, y - 1),
            (x + r - 1, y + 1),
            (x - r + 1, y + 1),
        ],
        fill=(123, 67, 36),
    )
    d.line((x - r + 2, y - 2, x + 1, y - 3, x + r - 1, y - 1), fill=(186, 116, 53))
    d.line((x - r + 1, y, x + r - 2, y), fill=(221, 166, 96))
    for q in (-2, 1, 3):
        d.point((x + q, y - 1), fill=(152, 88, 39))
cut = base.copy()
d = ImageDraw.Draw(cut)
for x, y in [(109, 90), (123, 93), (116, 100)]:
    d.line((x - 2, y, x + 2, y), fill=(51, 40, 46))
    d.line((x, y - 2, x, y), fill=(138, 93, 65))
    d.point((x, y - 2), fill=(196, 148, 100))
    d.point((x + 3, y - 1), fill=(136, 98, 68))
full.save(out / "master-full.png")

# No dedupe: each screen cell owns a pattern, so patch uploads cannot change
# another tile referencing the same pattern. Sprite storage is bank1:128+.
subprocess.run(
    [
        str(args.gbdk / "bin/png2hicolorgb"),
        str(out / "master-full.png"),
        "--type=3",
        "-L=adaptive-fast",
        "-R=adaptive-fast",
        "--nodedupe",
        "--csource",
        "--bank=2",
        "-o",
        "master.c",
    ],
    cwd=out,
    check=True,
)
# Keep the full source; the bottom eight pixels are reserved for a status window.
master_c = out / "master.c"
master_c.write_text(
    master_c.read_text().replace(".height_in_tiles = 18u", ".height_in_tiles = 17u")
)
tiles = (out / "master.til").read_bytes()
tilemap = (out / "master.map").read_bytes()
attrs = bytearray((out / "master.atr").read_bytes())
pal = (out / "master.pal").read_bytes()
assert len(tiles) == 5760 and len(pal) == 4640
# Foreground root fringe: actor heads can pass behind it, feet remain outside.
for y in (7, 8):
    for x in range(4, 8):
        attrs[y * 20 + x] |= 128
(out / "master.atr").write_bytes(attrs)


def colors_at(x, y):
    slot = attrs[(y // 8) * 20 + x // 8] & 7
    block = ((y + 1) // 2) * 64 if slot < 4 else (y // 2) * 64 + 32
    colors = struct.unpack_from("<4H", pal, block + (slot % 4) * 8)
    return [tuple(((v >> s) & 31) * 255 // 31 for s in (0, 5, 10)) for v in colors]


def pattern_id(cell):
    return tilemap[cell] + (256 if attrs[cell] & 8 else 0)


def decode(data):
    im = Image.new("RGB", (160, 144))
    for y in range(144):
        for x in range(160):
            cell = (y // 8) * 20 + x // 8
            offset = pattern_id(cell) * 16 + (y % 8) * 2
            k = ((data[offset] >> (7 - x % 8)) & 1) | (((data[offset + 1] >> (7 - x % 8)) & 1) << 1)
            im.putpixel((x, y), colors_at(x, y)[k])
    return im


decoded = decode(tiles)
decoded.save(out / "master-decoded.png")


def encode_cell(im, cx, cy):
    result = []
    for y in range(cy * 8, cy * 8 + 8):
        lo = hi = 0
        for x in range(cx * 8, cx * 8 + 8):
            target = im.getpixel((x, y))
            k = min(
                range(4),
                key=lambda n: sum((a - b) ** 2 for a, b in zip(target, colors_at(x, y)[n])),
            )
            lo = (lo << 1) | (k & 1)
            hi = (hi << 1) | (k >> 1)
        result.extend((lo, hi))
    return bytes(result)


resource_cells = [y * 20 + x for y in range(10, 13) for x in range(13, 17)]
reveal_cells = [y * 20 + x for y in range(8, 10) for x in range(9, 14)]
reveal = decoded.copy()
d = ImageDraw.Draw(reveal)
# Deliberate native pixels: fine branching roots. Quantize into the MASTER'S
# palette; no scene-wide recoloring and no independent image conversion.
for points in [
    [(73, 66), (77, 68), (79, 73), (86, 75), (92, 75), (98, 78), (107, 78)],
    [(83, 65), (86, 70), (86, 75)],
    [(97, 65), (94, 70), (92, 75)],
    [(108, 67), (103, 71), (98, 78)],
]:
    d.line(points, fill=(245, 230, 186))
    for x, y in points[1:-1]:
        d.point((x + 1, y), fill=(245, 230, 186))

data = ""


def arr(name, values, typ="uint8_t"):
    return f"const {typ} {name}[] = {{" + ",".join(str(x) for x in values) + "};\n"


data += arr("resource_ids", [pattern_id(c) for c in resource_cells], "uint16_t")
data += arr(
    "resource_full",
    b"".join(tiles[pattern_id(c) * 16 : pattern_id(c) * 16 + 16] for c in resource_cells),
)
data += arr("resource_cut", b"".join(encode_cell(cut, c % 20, c // 20) for c in resource_cells))
data += arr("reveal_ids", [pattern_id(c) for c in reveal_cells], "uint16_t")
data += arr(
    "reveal_off",
    b"".join(tiles[pattern_id(c) * 16 : pattern_id(c) * 16 + 16] for c in reveal_cells),
)
data += arr("reveal_on", b"".join(encode_cell(reveal, c % 20, c // 20) for c in reveal_cells))
data += arr("foreground_attrs", [attrs[y * 20 + x] for y in (7, 8) for x in range(4, 8)])

# Bram's native 16x16 cells. Two overlaid palette layers provide six opaque
# colors, using four 8x16 objects. Shared plum shadows and warm shelf highlights.
rows = [
    "................",
    "......334.......",
    ".....33344......",
    "....3333444.....",
    "....2333455.....",
    "....2331555.....",
    ".....221566.....",
    ".....222566.....",
    "....2232266.....",
    "...22233222.....",
    "...522333225....",
    "....2233322.....",
    ".....22222......",
    ".....22.22......",
    "....11..11......",
    "................",
]
rgb = [
    (0, 0, 0),
    (50, 38, 46),
    (81, 54, 52),
    (119, 65, 44),
    (169, 108, 61),
    (186, 151, 108),
    (213, 190, 144),
]
frames = []
for f in range(8):
    grid = [list(r) for r in rows]
    if f in (2, 3):  # back, hood covers face
        for y in range(4, 9):
            for x in range(8, 11):
                if grid[y][x] != ".":
                    grid[y][x] = "3" if x < 10 else "4"
    if f in (0, 1):  # front beard centered
        for y in range(6, 9):
            grid[y][7] = "5"
            grid[y][8] = "6"
            grid[y][9] = "5"
    if f in (1, 3, 5):
        grid[14][4] = "."
        grid[14][5] = "."
        grid[13][4] = "1"
        grid[14][8] = "."
        grid[14][10] = "1"
    if f == 7:
        grid[10][11] = "."
        grid[8][11] = "5"
        grid[7][12] = "6"
        grid[6][13] = "4"
    picture = Image.new("RGBA", (16, 16))
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            if c != ".":
                picture.putpixel((x, y), rgb[int(c)] + (255,))
    picture.save(out / f"bram-{f}.png")
    # 8x16 objects: each half stores upper then lower tile, base then highlights.
    for layer in range(2):
        for half in range(2):
            for y in range(16):
                lo = hi = 0
                for x in range(half * 8, half * 8 + 8):
                    c = 0 if grid[y][x] == "." else int(grid[y][x])
                    k = c if layer == 0 and c <= 3 else c - 3 if layer == 1 and c >= 4 else 0
                    lo = lo * 2 + (k & 1)
                    hi = hi * 2 + (k >> 1)
                frames.extend((lo, hi))
data += arr("bram_tiles", frames)
rgb555 = lambda c: sum((v * 31 // 255) << s for v, s in zip(c, (0, 5, 10)))
data += arr("actor_palettes", [rgb555(rgb[i]) for i in (0, 1, 2, 3, 0, 4, 5, 6)], "uint16_t")
# Brackets enclose exactly one selected 8x8 cell, including screen edges.
# The remaining sprite pixels are transparent; dark keylines survive bright art.
marker = []
cursor = Image.new("L", (16, 16))
cd = ImageDraw.Draw(cursor)
for x, y, dx, dy in [(1, 1, 1, 1), (6, 1, -1, 1), (1, 6, 1, -1), (6, 6, -1, -1)]:
    for q in range(2):
        cd.rectangle(
            (
                min(x, x + dx * q) - 1,
                min(y, y + dy * q) - 1,
                max(x, x + dx * q) + 1,
                max(y, y + dy * q) + 1,
            ),
            fill=1,
        )
for x, y, dx, dy in [(1, 1, 1, 1), (6, 1, -1, 1), (1, 6, 1, -1), (6, 6, -1, -1)]:
    cd.line((x, y, x + dx, y), fill=2)
    cd.line((x, y, x, y + dy), fill=2)
for half in range(2):
    for y in range(16):
        lo = hi = 0
        for x in range(half * 8, half * 8 + 8):
            k = cursor.getpixel((x, y))
            lo = lo * 2 + (k & 1)
            hi = hi * 2 + (k >> 1)
        marker.extend((lo, hi))
data += arr("cursor_tiles", marker)
data += arr(
    "cursor_palettes",
    [
        rgb555(c)
        for c in [
            (0, 0, 0),
            (50, 38, 46),
            (206, 181, 131),
            (150, 100, 60),
            (0, 0, 0),
            (50, 38, 46),
            (173, 77, 52),
            (150, 100, 60),
        ]
    ],
    "uint16_t",
)

# Distinct target pin (two work phases) and a luminous exposure knot. Each
# uses one hardware object; all objects together fit within a scanline's ten.
icons = []
for style in ("pin", "work", "knot", "knot-bright"):
    im = Image.new("L", (8, 16))
    pen = ImageDraw.Draw(im)
    if style in ("pin", "work"):
        pen.polygon([(3, 1), (6, 4), (3, 8), (0, 4)], fill=1)
        pen.polygon([(3, 2), (5, 4), (3, 6), (1, 4)], fill=2)
        if style == "work":
            pen.line((2, 4, 4, 4), fill=3)
    else:
        pen.ellipse((0, 3, 6, 9), fill=1)
        pen.ellipse((1, 4, 5, 8), outline=2)
        pen.point((3, 6), fill=3)
        if style == "knot-bright":
            for pt in [(3, 1), (3, 11), (7, 6)]:
                pen.point(pt, fill=2)
    for y in range(16):
        lo = hi = 0
        for x in range(8):
            k = im.getpixel((x, y))
            lo = lo * 2 + (k & 1)
            hi = hi * 2 + (k >> 1)
        icons.extend((lo, hi))
data += arr("icon_tiles", icons)
data += arr(
    "reveal_palette",
    [rgb555(c) for c in [(0, 0, 0), (31, 41, 53), (92, 185, 184), (216, 238, 206)]],
    "uint16_t",
)

# Compact explicitly authored 3x5 text, one 8x8 hardware tile per glyph.
glyphs = {
    " ": "000000000000000",
    "A": "010101111101101",
    "B": "110101110101110",
    "C": "011100100100011",
    "D": "110101101101110",
    "E": "111100110100111",
    "F": "111100110100100",
    "G": "011100101101011",
    "H": "101101111101101",
    "I": "111010010010111",
    "J": "001001001101010",
    "K": "101101110101101",
    "L": "100100100100111",
    "M": "101111111101101",
    "N": "101111111111101",
    "O": "010101101101010",
    "P": "110101110100100",
    "Q": "010101101111011",
    "R": "110101110101101",
    "S": "011100010001110",
    "T": "111010010010010",
    "U": "101101101101111",
    "V": "101101101101010",
    "W": "101101111111101",
    "X": "101101010101101",
    "Y": "101101010010010",
    "Z": "111001010100111",
    "0": "111101101101111",
    "1": "010110010010111",
    "2": "110001010100111",
    "3": "110001010001110",
    "4": "101101111001001",
    "5": "111100110001110",
    "6": "011100111101111",
    "7": "111001010010010",
    "8": "111101111101111",
    "9": "111101111001110",
    ":": "000010000010000",
    "+": "000010111010000",
    "-": "000000111000000",
}
charset = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:+-"
font = []
for ch in charset:
    for y in range(8):
        bits = int(glyphs[ch][(y - 1) * 3 : y * 3], 2) << 3 if 1 <= y <= 5 else 0
        font.extend((bits, bits))
data += arr("hud_font", font)
data += "#define HUD_FONT_COUNT " + str(len(charset)) + "\n"

# Feet positions on an 8px navigation grid. Hand-reviewed clearing only; bridge
# and exits stay scenery in this bounded experiment. Rocks and resource block it.
walk = []
for y in range(18):
    for x in range(20):
        valid = (9 <= y <= 15 and 5 <= x <= 16) or (y == 8 and 8 <= x <= 16)
        if (x in (12, 13) and y in (10, 11)) or (13 <= x <= 16 and 10 <= y <= 12):
            valid = False
        if x in (6, 7) and y == 11:
            valid = False
        walk.append(int(valid))
data += arr("walkable", walk)
# Compute routes once, matching the main game's precomputed-route approach.
# The native loop performs a bounded table lookup, with no search/initialization.
cells = [i for i, v in enumerate(walk) if v]
index = {c: i for i, c in enumerate(cells)}
routes = [255] * (len(cells) ** 2)
for start in cells:
    seen = {start: 4}
    q = deque([start])
    while q:
        c = q.popleft()
        for direction, n in enumerate((c - 1, c + 1, c - 20, c + 20)):
            if n not in index or n in seen or abs(n % 20 - c % 20) + abs(n // 20 - c // 20) != 1:
                continue
            seen[n] = direction if c == start else seen[c]
            q.append(n)
    for goal, direction in seen.items():
        routes[index[start] * len(cells) + index[goal]] = direction
route_c = (
    "#pragma bank 3\n#include <gbdk/platform.h>\n"
    + arr("cell_index", [index.get(c, 255) for c in range(360)])
    + arr("directions", routes)
)
route_c += (
    "uint8_t route_step(uint8_t sx,uint8_t sy,uint8_t tx,uint8_t ty) BANKED { uint8_t a=cell_index[(uint16_t)sy*20+sx],b=cell_index[(uint16_t)ty*20+tx]; if(a==255||b==255)return 255; return directions[(uint16_t)a*"
    + str(len(cells))
    + "+b]; }\n"
)
(out / "routes.c").write_text(route_c)
(out / "assets.h").write_text(data)
renderer = ROOT.parent / "hearth-hicolor/src"
rom = out / "heartwood-playable.gbc"
subprocess.run(
    [
        str(args.gbdk / "bin/lcc"),
        "-Wm-yC",
        "-Wl-yt0x19",
        "-Wl-m",
        "-Wl-w",
        "-autobank",
        "-Wb-ext=.rel",
        "-I" + str(renderer),
        "-I.",
        "-o",
        str(rom),
        str(ROOT / "src/main.c"),
        str(renderer / "gbc_hicolor.c"),
        "master.c",
        "routes.c",
    ],
    cwd=out,
    check=True,
)
manifest = {
    "source": str(args.source),
    "sourceSHA256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
    "romSHA256": hashlib.sha256(rom.read_bytes()).hexdigest(),
    "romBytes": rom.stat().st_size,
    "masterBytes": len(tiles) + len(tilemap) + len(attrs) + len(pal),
    "resourcePatchBytesPerState": len(resource_cells) * 16,
    "revealPatchBytesPerState": len(reveal_cells) * 16,
    "spriteTileBytes": len(frames) + len(marker),
    "paletteBytes": len(pal),
    "foregroundPriorityCells": [[x, y] for y in (7, 8) for x in range(4, 8)],
}
manifest.update(
    {
        "routingBytes": len(routes) + 360,
        "hudFontBytes": len(font),
        "iconBytes": len(icons),
        "imageHeight": 136,
        "maxObjectsPerScanline": 8,
    }
)
(out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))

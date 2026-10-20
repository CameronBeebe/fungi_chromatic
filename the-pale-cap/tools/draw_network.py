"""Deterministic native pixel art and animation cels for the mycelial chapter."""

from pathlib import Path
from collections import deque
import json, math
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
# Reuse the authored room primitives without publishing the previous asset.
source = (ROOT / "tools/draw_grotto.py").read_text().split("im.save(ROOT/")[0]
env = {"__file__": str(ROOT / "tools/draw_grotto.py")}
exec(compile(source, "grotto primitives", "exec"), env)
im, d, slots, solid, INK = [env[k] for k in ("im", "d", "slots", "solid", "INK")]
nodes = [
    {"id": "spring", "name": "Pool root", "x": 10, "y": 20},
    {"id": "forge", "name": "Forge root", "x": 23, "y": 15},
    {"id": "crown", "name": "Crown root", "x": 15, "y": 10},
]


def path(a, b):
    queue = deque([a])
    prev = {a: None}
    while queue:
        p = queue.popleft()
        if p == b:
            break
        for dx, dy in [(0, -1), (1, 0), (-1, 0), (0, 1)]:
            q = (p[0] + dx, p[1] + dy)
            if 2 <= q[0] < 30 and 2 <= q[1] < 26 and q not in solid and q not in prev:
                prev[q] = p
                queue.append(q)
    out = []
    p = b
    while p is not None:
        out.append(p)
        p = prev[p]
    return out[::-1]


# A connected tree with a source at the pool, forge relay and crown nexus.
routes = [
    path((11, 21), (16, 21)),
    path((16, 21), (24, 16)),
    path((24, 16), (20, 13)),
    path((20, 13), (16, 11)),
]
network = set(p for route in routes for p in route)
for x, y in list(network):
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)]:
        q = (x + dx, y + dy)
        if (
            2 <= q[0] < 30
            and 2 <= q[1] < 26
            and q not in solid
            and (x + dx // 2, y + dy // 2) not in solid
        ):
            network.add(q)
for x, y in sorted(network):
    slots[y][x] = 6
    im.paste(INK[0], (x * 8, y * 8, x * 8 + 8, y * 8 + 8))
    a, b = x * 8, y * 8
    # Fine repeating branching tissue below the broad conducting strands.
    p = (x + y) % 3
    d.line([(a, b + 7), (a + 3, b + 4), (a + 3, b + 2), (a + 5, b)], fill=INK[1 + p])
    d.line([(a + 3, b + 4), (a + 6, b + 4), (a + 7, b + 2)], fill=INK[1 + (p + 1) % 3])
    d.point((a + 1, b + 2), fill=INK[1 + p])
for ri, route in enumerate(routes):
    for j, (x, y) in enumerate(route):
        a, b = x * 8 + 4, y * 8 + 4
        if j + 1 < len(route):
            q = route[j + 1]
            end = (q[0] * 8 + 4, q[1] * 8 + 4)
            d.line([(a, b), end], fill=INK[1], width=3)
            d.line([(a, b), end], fill=INK[2])
            for k in range(8):
                px = a + (end[0] - a) * k // 8
                py = b + (end[1] - b) * k // 8
                d.point((px, py), fill=INK[1 + (k + j) % 3])
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if (x + dx, y + dy) in network:
                d.line(
                    [(a, b), (a + dx * 5 - dy * 2, b + dy * 5 + dx * 2), (a + dx * 8, b + dy * 8)],
                    fill=INK[1 + (j + ri) % 3],
                )
    # Hair-fine spore rosettes along the route.
    for x, y in route[::3]:
        a, b = x * 8 + 4, y * 8 + 4
        for dx, dy in [(2, 0), (-2, 0), (0, 2), (0, -2)]:
            d.point((a + dx, b + dy), fill=INK[3])
# More deliberate cap structure: radial gills and concentric scalloped ridges.
for x in range(94, 164, 3):
    d.line([(x, 51), (127 + (x - 128) // 5, 66)], fill=INK[1 if x % 2 else 3])
for y in range(26, 48):
    for x in range(94, 162):
        rx = (x - 128) / 36
        ry = (y - 46) / 22
        radius = math.sqrt(rx * rx + ry * ry)
        if radius < 0.91:
            angle = math.atan2(ry, rx)
            band = int(radius * 13 + math.sin(angle * 7) * 0.75) % 5
            if band in (0, 1):
                d.point((x, y), fill=INK[1 if band == 0 else 3])
# Lichen/crystal detail on the walls, never in the walking space.
for x, y in sorted(solid):
    if slots[y][x] == 0 and (x * 3 + y * 5) % 7 == 0:
        a, b = x * 8, y * 8
        d.line([(a + 2, b + 5), (a + 3, b + 2), (a + 5, b + 4)], fill=INK[2])
        d.point((a + 3, b + 1), fill=INK[3])


def cel(kind, phase, identity=0):
    out = Image.new("RGB", (16, 16), INK[0])
    p = ImageDraw.Draw(out)
    if kind == "seed":
        p.ellipse((3, 3, 12, 12), outline=INK[1])
        p.line([(7, 5), (10, 8), (7, 11), (5, 8), (7, 5)], fill=INK[2])
        p.point((7, 7), fill=INK[3])
        p.point((8, 8), fill=INK[3])
    else:
        for y in range(16):
            for x in range(16):
                dx = x - 7.5
                dy = y - 7.5
                r = math.hypot(dx, dy)
                a = math.atan2(dy, dx)
                edge = 6.4 + 1.0 * math.cos(a * 6 + phase * math.pi / 2)
                if r < edge:
                    wave = int(r * 1.5 + phase + math.cos(a * 4 + phase * 0.7)) % 4
                    out.putpixel((x, y), tuple(bytes.fromhex(INK[1 + wave % 3][1:])))
        p.ellipse((5, 5, 10, 10), fill=INK[0], outline=INK[3])
        p.rectangle((7, 6, 8, 9), fill=INK[2 if phase % 2 else 3])
    # Distinct corner registration marks prevent compiler tile aliasing between
    # targets. These pixels are also part of every animation cel.
    for ox, oy in [(0, 0), (8, 0), (0, 8), (8, 8)]:
        p.point((ox + identity % 3, oy), fill=INK[1])
        p.point((ox + (identity + 1) % 3, oy + 1), fill=INK[2])
    return out


# Each 16px target has its own two-row atlas block, with dormant + four blooms.
atlas = Image.new("RGB", (128, 64), INK[0])
animation = []
for i, node in enumerate(nodes + [{"id": "eye", "x": 15, "y": 4}]):
    for phase in range(5):
        atlas.paste(
            cel("seed" if phase == 0 and i < 3 else "bloom", phase, i), (phase * 16, i * 16)
        )
    im.paste(cel("seed" if i < 3 else "bloom", 0, i), (node["x"] * 8, node["y"] * 8))
    for yy in range(node["y"], node["y"] + 2):
        for xx in range(node["x"], node["x"] + 2):
            slots[yy][xx] = 4
    animation.append({**node, "baseIndex": i * 32})
# A real signal route, oriented outward from the nexus, like the terminal.
signal = []
for route in reversed(routes):
    for pos in reversed(route):
        if not signal or pos != signal[-1]:
            signal.append(pos)
# Exclude knot tiles: their own cels communicate the permanent core state.
occupied = {(n["x"] + dx, n["y"] + dy) for n in nodes for dx in range(2) for dy in range(2)}
signal = [pos for pos in signal if pos not in occupied]
pulse_atlas = Image.new("RGB", (128, ((len(signal) * 2 + 15) // 16) * 8), INK[0])
for i, (x, y) in enumerate(signal):
    # Unique lower-edge signatures prevent global changes through tile dedup.
    for bit in range(7):
        d.point((x * 8 + bit, y * 8 + 7), fill=INK[1 if i & (1 << bit) else 0])
    original = im.crop((x * 8, y * 8, x * 8 + 8, y * 8 + 8))
    bright = original.copy()
    bd = ImageDraw.Draw(bright)
    bd.line([(4, 0), (7, 3), (4, 6), (1, 3), (4, 0)], fill=INK[3])
    bd.rectangle((3, 2, 5, 4), fill=INK[3])
    for k, frame in enumerate([original, bright]):
        idx = i * 2 + k
        pulse_atlas.paste(frame, ((idx % 16) * 8, (idx // 16) * 8))
im.save(ROOT / "assets/backgrounds/living-grotto.png")
signal_id = "37cf484d-f160-407d-acfc-21b841499c70"
pulse_atlas.save(ROOT / "assets/tilesets/nexus-signal.png")
signal_meta = {
    "_resourceType": "tileset",
    "id": signal_id,
    "name": "Nexus Signal",
    "symbol": "tileset_nexus_signal",
    "filename": "nexus-signal.png",
    "width": 16,
    "height": pulse_atlas.height // 8,
    "imageWidth": 128,
    "imageHeight": pulse_atlas.height,
}
(ROOT / "assets/tilesets/nexus-signal.png.gbsres").write_text(
    json.dumps(signal_meta, indent=2) + "\n"
)
atlas.save(ROOT / "assets/tilesets/mycelial-cels.png")
meta = {
    "_resourceType": "tileset",
    "id": "c79580e8-21a1-446c-90a1-6e3b0d0a30b1",
    "name": "Mycelial Cels",
    "symbol": "tileset_mycelial_cels",
    "filename": "mycelial-cels.png",
    "width": 16,
    "height": 8,
    "imageWidth": 128,
    "imageHeight": 64,
}
(ROOT / "assets/tilesets/mycelial-cels.png.gbsres").write_text(json.dumps(meta, indent=2) + "\n")
layout = {
    "nodes": nodes,
    "routes": routes,
    "network": sorted(network),
    "slots": slots,
    "solid": sorted(solid),
    "animation": animation,
    "tilesetId": meta["id"],
    "signal": signal,
    "signalTilesetId": signal_id,
}
(ROOT / "art/network-layout.json").write_text(json.dumps(layout, indent=2) + "\n")
# Static art proof only. Actual motion must be verified on the ROM.
pal = env["PAL"]
pal[6] = ["17182f", "8848d8", "30d8c0", "ffe090"]
pal[4] = ["282040", "7850b0", "d098e8", "fff0cf"]
proof = im.copy()
colors = [tuple(bytes.fromhex(c[1:])) for c in INK]
for y in range(224):
    for x in range(256):
        proof.putpixel(
            (x, y),
            tuple(bytes.fromhex(pal[slots[y // 8][x // 8]][colors.index(im.getpixel((x, y)))])),
        )
proof.resize((768, 672), Image.Resampling.NEAREST).save(ROOT / "art/network-proof.png")
print(f"{len(network)} network tiles; four animated 16x16 targets; five cels each.")

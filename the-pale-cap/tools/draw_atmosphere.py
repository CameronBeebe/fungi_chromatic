"""Native four-shade atmosphere art. Keeps terrain, root and signal tiles intact."""

from pathlib import Path
import json, math
from PIL import Image, ImageDraw

P = Path(__file__).resolve().parents[1]
INK = ["#071821", "#306850", "#86c06c", "#e0f8cf"]
im = Image.open(P / "assets/backgrounds/living-grotto.png").convert("RGB")
d = ImageDraw.Draw(im)
l = json.loads((P / "art/network-layout.json").read_text())
slots = l["slots"]
solid = set(map(tuple, l["solid"]))
protected = set(map(tuple, l["network"])) | set(map(tuple, l["signal"]))
for node in l["animation"]:
    for dy in range(2):
        for dx in range(2):
            protected.add((node["x"] + dx, node["y"] + dy))
# Reusable stone textures: seams, mineral inclusions, small hanging shelves.
for y in range(28):
    for x in range(32):
        if (x, y) in protected:
            continue
        a, b = x * 8, y * 8
        if slots[y][x] == 0 and (x, y) in solid:
            k = (x + 2 * y) % 4
            if k == 0:
                d.line([(a + 2, b + 1), (a + 3, b + 3), (a + 2, b + 5)], fill=INK[0])
                d.point((a + 4, b + 2), fill=INK[2])
            elif k == 1:
                d.line([(a + 1, b + 5), (a + 3, b + 3), (a + 5, b + 4)], fill=INK[2])
                d.point((a + 3, b + 2), fill=INK[3])
        elif slots[y][x] == 1 and (x, y) not in solid and (x + 3 * y) % 9 == 0:
            d.line([(a + 1, b + 7), (a + 2, b + 4), (a + 3, b + 6), (a + 5, b + 5)], fill=INK[1])
            d.point((a + 2, b + 4), fill=INK[2])
# Coral caps: scalloped edges, gills, spores and shaded stems, same footprint.
for x, y in [(5, 7), (25, 4), (27, 21), (3, 24), (22, 22)]:
    a, b = x * 8, y * 8
    for k in range(4, 21, 3):
        d.line([(a + k, b + 13), (a + 11 + (k - 11) // 3, b + 17)], fill=INK[1])
    d.line([(a + 10, b + 16), (a + 10, b + 21)], fill=INK[1])
    d.point((a + 12, b + 18), fill=INK[3])
    for ox, oy in [(5, 9), (12, 4), (17, 10)]:
        d.point((a + ox, b + oy), fill=INK[3])
# Copper masonry, rivets, throat arch and foundation make the forge legible.
for y in range(76, 101, 5):
    for x in [194, 225]:
        d.line([(x, y), (x + 4, y)], fill=INK[2])
        d.point((x + 1, y + 1), fill=INK[0])
d.line([(200, 95), (200, 86), (204, 83), (219, 83), (223, 87), (223, 98)], fill=INK[2])
for x in range(194, 232, 5):
    d.point((x, 102), fill=INK[1])
d.line([(211, 57), (211, 71)], fill=INK[3])
d.line([(220, 58), (220, 72)], fill=INK[0])
# Small pale fruiting bodies under the great cap, entirely within its footprint.
for x in (87, 99, 151, 165):
    d.line([(x, 66), (x, 69)], fill=INK[1])
    d.line([(x - 2, 65), (x + 2, 65)], fill=INK[2])
    d.point((x, 64), fill=INK[3])
# Banks/reeds stay on already blocked pool cells.
for y in [14, 17, 20]:
    d.line([(66, y * 8 + 6), (67, y * 8 + 2), (69, y * 8 + 6)], fill=INK[2])

# Animated individual cells have explicit unique index signatures so tile
# replacement cannot animate unrelated deduplicated floor or signal art.
specs = [
    ("water", 4, 14),
    ("water", 6, 17),
    ("water", 4, 20),
    ("ember", 26, 11),
    ("ember", 27, 11),
    ("breath", 6, 7),
    ("breath", 26, 4),
    ("breath", 28, 21),
    ("breath", 23, 22),
    ("spore", 8, 8),
    ("spore", 24, 5),
    ("spore", 25, 21),
    ("spore", 9, 23),
    ("glyph", 13, 10),
    ("glyph", 22, 10),
    ("glyph", 13, 12),
    ("ember", 25, 11),
]
atlas = Image.new("RGB", (128, ((len(specs) * 5 + 15) // 16) * 8), INK[0])
targets = []
for i, (kind, x, y) in enumerate(specs):
    assert (x, y) not in protected, (kind, x, y)
    original = im.crop((x * 8, y * 8, x * 8 + 8, y * 8 + 8))
    frames = []
    for phase in range(5):
        out = original.copy()
        q = ImageDraw.Draw(out)
        if phase:
            t = (phase - 1 + i) % 4 if kind == "ember" else phase - 1
            if kind == "water":
                q.rectangle((0, 0, 7, 6), fill=INK[1])
                q.line([((t + 1) % 4, 2), (min(7, 4 + t), 2)], fill=INK[2])
                q.line([(max(0, 3 - t), 5), (6 - t, 5)], fill=INK[3 if t == 1 else 2])
            elif kind == "ember":
                q.rectangle((0, 0, 7, 6), fill=INK[0])
                q.polygon([(0, 6), (2, 3 + t % 2), (3, t % 3), (5, 4), (6, 2), (7, 6)], fill=INK[2])
                q.line([(3, 6), (3, 3 + t % 2), (5, 6)], fill=INK[3])
            elif kind == "breath":
                q.line(
                    [(1, 5 + t % 2), (3, 3 + t % 2), (6, 3 + t % 2)], fill=INK[3 if t == 1 else 2]
                )
                q.point((5, 1), fill=INK[3 if t == 2 else 2])
            elif kind == "spore":
                q.point(((2 + i + t // 2) % 7, 6 - t * 2), fill=INK[2 if t % 2 else 3])
                q.point(((5 + i - t) % 7, (3 - t) % 7), fill=INK[1])
            elif kind == "glyph":
                # Repeated vocabulary: aperture, fork, vessel, returning eye.
                q.rectangle((0, 0, 7, 6), fill=INK[0])
                g = (t + i) % 4
                forms = [
                    [(1, 3), (3, 1), (5, 3), (3, 5), (1, 3)],
                    [(1, 1), (3, 3), (5, 1), (3, 3), (3, 6)],
                    [(1, 1), (1, 5), (5, 5), (5, 1)],
                    [(1, 4), (3, 2), (5, 4)],
                ]
                q.line(forms[g], fill=INK[3])
                q.point((3, 3), fill=INK[2])
        # Signature kept in every cel, including its initial background instance.
        for bit in range(8):
            q.point((bit, 7), fill=INK[1 if (i + 1) & (1 << bit) else 0])
        frames.append(out)
        idx = i * 5 + phase
        atlas.paste(out, ((idx % 16) * 8, (idx // 16) * 8))
    im.paste(frames[0], (x * 8, y * 8))
    targets.append({"kind": kind, "x": x, "y": y, "baseIndex": i * 5})
im.save(P / "assets/backgrounds/whispering-grotto.png")
atlas.save(P / "assets/tilesets/atmosphere-cels.png")
meta = {
    "_resourceType": "tileset",
    "id": "atmosphere-cels",
    "name": "Atmosphere cels",
    "symbol": "tileset_atmosphere_cels",
    "filename": "atmosphere-cels.png",
    "width": 16,
    "height": atlas.height // 8,
    "imageWidth": 128,
    "imageHeight": atlas.height,
}
(P / "assets/tilesets/atmosphere-cels.png.gbsres").write_text(json.dumps(meta, indent=2) + "\n")
(P / "art/atmosphere-layout.json").write_text(
    json.dumps({"targets": targets, "tilesetId": meta["id"]}, indent=2) + "\n"
)
print(len(specs), "animated cells; collision and network layout unchanged")

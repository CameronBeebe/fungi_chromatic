from pathlib import Path
from PIL import Image
import re, json, hashlib

r = Path(__file__).resolve().parent
h = (r / "art.h").read_text()
old = (r / "reference/baseline-art.h").read_text()


def array(s, n):
    return list(map(int, re.search(n + r"\[\] = \{([^}]+)", s)[1].split(",")))


tiles = array(h, "art_tiles")
m = array(h, "art_map")
a = array(h, "art_attrs")
p = array(h, "art_palettes")
bt = array(old, "art_tiles")
bm = array(old, "art_map")
ba = array(old, "art_attrs")
audit = json.loads((r / "audit.json").read_text())
assert len(tiles) == 206 * 16
assert len(set(tuple(tiles[i : i + 16]) for i in range(0, len(tiles), 16))) == 206
assert len(m) == len(a) == 360 and max(m) < 206 and set(a) == set(range(8))
assert len(p) == 96 and max(p) <= 32767
for t in audit["retainedForkTiles"]:
    assert tiles[m[t] * 16 : m[t] * 16 + 16] == bt[bm[t] * 16 : bm[t] * 16 + 16] and a[t] == ba[t]
counts = []
for theme, name in enumerate(["01-vermilion", "02-saffron", "03-rose"]):
    im = Image.open(r / (name + ".png")).convert("RGB")
    maximum = 0
    raw = []
    for y in range(144):
        for x in range(160):
            t = y // 8 * 20 + x // 8
            o = m[t] * 16 + (y % 8) * 2
            shift = 7 - x % 8
            index = ((tiles[o] >> shift) & 1) | (((tiles[o + 1] >> shift) & 1) << 1)
            c = p[theme * 32 + a[t] * 4 + index]
            rgb = tuple(round(v * 255 / 31) for v in [c & 31, c >> 5 & 31, c >> 10 & 31])
            assert im.getpixel((x, y)) == rgb
            raw.append(tuple(v * 8 for v in [c & 31, c >> 5 & 31, c >> 10 & 31]))
    for ty in range(18):
        for tx in range(20):
            maximum = max(
                maximum, len(set(im.crop((tx * 8, ty * 8, tx * 8 + 8, ty * 8 + 8)).getdata()))
            )
    assert maximum <= 4
    actual = Image.open(
        r / "emulator-evidence" / ["01-boot-vermilion.png", "03-saffron.png", "04-rose.png"][theme]
    ).convert("RGB")
    assert list(actual.getdata()) == raw, "PyBoy RGB555 expansion does not match decoded native art"
    counts.append(
        {
            "name": name,
            "maxTileColors": maximum,
            "all23040PixelsMatchDecodedSource": True,
            "all23040EmulatorPixelsMatchRGB555Times8": True,
        }
    )
(r / "native-verification.json").write_text(
    json.dumps(
        {
            "uniqueTiles": 206,
            "bank": 0,
            "tileBytes": 3296,
            "mapBytes": 360,
            "attributeBytes": 360,
            "palettesPerTheme": 8,
            "retainedForkTilesExactlyIdentical": len(audit["retainedForkTiles"]),
            "variants": counts,
        },
        indent=2,
    )
)
print(
    "All tiles, retained fork indices, three source images and three actual emulator framebuffers verified."
)

"""Reproducible ROM checks, actual framebuffer captures, and bounded controller tests."""

from pathlib import Path
from pyboy import PyBoy
from PIL import Image, ImageChops, ImageDraw
import hashlib, json, re

root = Path(__file__).resolve().parent
out = root / "emulator-evidence"
out.mkdir(exist_ok=True)
rom = root / "gillsong-refinement.gbc"
b = rom.read_bytes()
header = 0
for v in b[0x134:0x14D]:
    header = (header - v - 1) & 255
assert header == b[0x14D]
assert (sum(b) - b[0x14E] - b[0x14F]) & 65535 == int.from_bytes(b[0x14E:0x150], "big")
assert b[0x143] == 0xC0
p = PyBoy(str(rom), window="null", sound_emulated=False)
p.set_emulation_speed(0)
p.tick(120, True)


def shot(n):
    im = p.screen.image.copy().convert("RGB")
    im.save(out / (n + ".png"))
    return im


def press(k):
    p.button_press(k)
    p.tick(2, True)
    p.button_release(k)
    p.tick(2, True)


a = shot("01-boot-vermilion")
print("boot", a.getpixel((0, 0)), flush=True)
p.tick(60, True)
assert ImageChops.difference(a, shot("02-still-after-60")).getbbox() is None
press("right")
s = shot("03-saffron")
assert ImageChops.difference(a, s).getbbox()
press("right")
r = shot("04-rose")
assert ImageChops.difference(s, r).getbbox()
press("right")
assert ImageChops.difference(a, shot("05-right-wrap")).getbbox() is None
press("left")
assert ImageChops.difference(r, shot("06-left-wrap")).getbbox() is None
press("select")
assert ImageChops.difference(a, shot("07-select-wrap")).getbbox() is None
press("a")
frames = []
changed = set()
for i in range(192):
    p.tick(1, True)
    im = p.screen.image.copy().convert("RGB")
    frames.append(im)
    for j, (v, w) in enumerate(zip(a.getdata(), im.getdata())):
        if v != w:
            changed.add((j % 160, j // 160))
    if i in [0, 8, 16, 24, 32, 40, 48, 96, 191]:
        im.save(out / f"flow-{i:03}.png")
assert changed
h = (root / "art.h").read_text()
attrs = list(map(int, re.search(r"art_attrs\[\] = \{([^}]+)", h)[1].split(",")))
assert all(
    attrs[y // 8 * 20 + x // 8] == 6 for x, y in changed
), "Animation leaked outside ornament palette"
press("b")
assert ImageChops.difference(a, shot("08-b-restores-still")).getbbox() is None
p.tick(60, True)
assert ImageChops.difference(a, shot("09-b-remains-still")).getbbox() is None
# Retain actual ROM frames, not host reconstruction animation.
frames[0].save(
    out / "ornament-flow.gif",
    save_all=True,
    append_images=frames[1:],
    duration=17,
    loop=0,
    optimize=False,
)
strip = Image.new("RGB", (160 * 6, 170), (18, 24, 35))
d = ImageDraw.Draw(strip)
for col, i in enumerate([0, 8, 16, 24, 40, 96]):
    strip.paste(frames[i], (col * 160, 24))
    d.text((col * 160 + 5, 5), f"ROM frame +{i}", fill="white")
strip.save(out / "animation-contact-sheet.png")
report = {
    "romSHA256": hashlib.sha256(b).hexdigest(),
    "romBytes": len(b),
    "headerChecksum": True,
    "globalChecksum": True,
    "cgbOnly": True,
    "emulator": "PyBoy 2.7.0",
    "bootFrames": 120,
    "checks": [
        "static boot remains identical after 60 frames",
        "right cycles three palettes and wraps",
        "left wraps backward",
        "select cycles forward",
        "A starts localized animation",
        "192 consecutive animation frames checked",
        "all changed pixels use palette 6",
        "B restores exact boot framebuffer and remains still for 60 frames",
    ],
    "animatedPixelCount": len(changed),
    "physicalHardwareTested": False,
    "browserTested": False,
}
(out / "verification.json").write_text(json.dumps(report, indent=2))
p.stop(save=False)
print(json.dumps(report, indent=2))

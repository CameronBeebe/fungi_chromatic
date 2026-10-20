"""Exercise all six gallery views through real ROM input, using PyBoy."""

from pathlib import Path
import hashlib, json, shutil, tempfile
from pyboy import PyBoy

ROOT = Path(__file__).resolve().parent
rom = ROOT / "build/overworld-gallery.gbc"
out = ROOT / "build/evidence"
out.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "gallery.gbc"
    shutil.copy2(rom, path)
    p = PyBoy(str(path), window="null", sound_emulated=False)
    p.set_emulation_speed(0)
    p.tick(180, True)

    def press(key):
        p.button_press(key)
        p.tick(2, True)
        p.button_release(key)
        p.tick(60, True)

    p.screen.image.save(out / "00-help.png")
    press("start")
    fingerprints = []
    colors = []
    for direction in range(3):
        for exposure in range(2):
            picture = p.screen.image.copy()
            picture.save(out / f"{direction+1}-{exposure}.png")
            pixel_bytes = picture.tobytes()
            fingerprints.append(hashlib.sha256(pixel_bytes).hexdigest())
            count = len(set(picture.getdata()))
            colors.append(count)
            assert count > 100, ("Image not displayed", direction, exposure, count)
            for _ in range(180):
                p.tick(1, True)
                assert p.screen.image.tobytes() == pixel_bytes, "Unstable gallery frame"
            press("start")
            p.screen.image.save(out / f"help-{direction+1}-{exposure}.png")
            press("start")
            assert p.screen.image.tobytes() == pixel_bytes, "Help return changed image"
            press("a")
        press("right")
    assert len(set(fingerprints)) == 6, "Repeated or missing image"
    assert (
        hashlib.sha256(p.screen.image.tobytes()).hexdigest() == fingerprints[0]
    ), "Right wrap failed"
    press("left")
    assert (
        hashlib.sha256(p.screen.image.tobytes()).hexdigest() == fingerprints[4]
    ), "Left wrap failed"
    press("b")
    assert (
        hashlib.sha256(p.screen.image.tobytes()).hexdigest() == fingerprints[5]
    ), "B exposure toggle failed"
    p.stop(save=False)
report = {
    "romSHA256": hashlib.sha256(rom.read_bytes()).hexdigest(),
    "frameHashes": fingerprints,
    "colors": colors,
    "stableFramesPerImage": 180,
    "helpRoundTrips": 6,
    "allViewsUnique": True,
    "wrapAndBothExposureButtons": True,
    "physicalHardwareTested": False,
}
(out / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))

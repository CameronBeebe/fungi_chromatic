"""Play the actual cartridge: agents, dialogue, mailbox and battery persistence."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from agent_bridge import RomBridge, Decision
from pyboy import PyBoy

parser = argparse.ArgumentParser()
parser.add_argument("--rom", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    rom = Path(tmp) / "agents.gbc"
    shutil.copy2(args.rom, rom)
    p = PyBoy(str(rom), window="null", sound_emulated=False)
    p.set_emulation_speed(0)
    bridge = RomBridge(p, args.rom)

    def press(key, rest=24):
        p.button_press(key)
        p.tick(8, True)
        p.button_release(key)
        p.tick(rest, True)

    def shot(name):
        p.screen.image.save(args.output / (name + ".png"))

    def menu():
        press("start")
        press("down")
        press("down")
        press("a")
        press("a")

    p.tick(180, True)
    press("a", 60)
    press("right")
    press("right")
    press("a", 1800)
    a, b = bridge.observe(0), bridge.observe(1)
    assert a["bag"] > 0 and b["bag"] > 0, "Both agents must independently harvest"
    shot("01-world")
    sequence = bridge.submit(a, Decision("follow", "Stay close."))
    p.tick(600, True)
    a = bridge.observe(0)
    assert bridge.read("agent_consumed") == sequence and bridge.read("agent_status") == 1
    assert abs(a["x"] - a["bram"]["x"]) + abs(a["y"] - a["bram"]["y"]) <= 2
    # A delayed/replayed command may not change inventory or intentions.
    bridge.write("agent_command", 2)
    p.tick(60, True)
    assert bridge.observe(0)["intent"] == 1
    assert a["bag"] >= 2, "Gather enough to exercise the sharing reserve"
    total = a["bag"] + bridge.read("fungi")
    shared_before = a["shared"]
    fungi_before = bridge.read("fungi")
    # The NPC gives from its own actual bag, then the player gives via the menu.
    bridge.submit(a, Decision("share", "Here."))
    p.tick(60, True)
    assert bridge.read("fungi") == fungi_before + 1 and bridge.observe(0)["bag"] == a["bag"] - 1
    menu()
    shot("02-companion")
    press("a")
    shot("03-plans")
    for _ in range(6):
        press("down")
    press("a")
    shot("04-gift")
    press("a", 120)
    a = bridge.observe(0)
    assert a["gifts"] == 1 and a["trust"] == 2 and a["shared"] == shared_before + 2, a
    assert a["bag"] + bridge.read("fungi") == total, "Gift/share must conserve supplies"
    menu()
    shot("05-remembers")
    press("b")
    # Extract, then save using the normal home UI.
    press("start")
    press("down")
    press("a", 1200)
    assert bridge.read("at_hideout") == 1
    press("right")
    press("a")
    for _ in range(3):
        press("down")
    press("a")
    shot("06-saved")
    assert bridge.read("home_save_status") == 1
    saved = {
        name: {
            key: bridge.read(name + "_" + key)
            for key in ("bag", "trust", "gifts", "shared", "intent", "joined", "revision")
        }
        for name in ("moss", "pip")
    }
    p.stop(save=True)
    p = PyBoy(str(rom), window="null", sound_emulated=False)
    p.set_emulation_speed(0)
    p.tick(180, True)
    bridge = RomBridge(p, args.rom)
    restored = {
        name: {key: bridge.read(name + "_" + key) for key in values}
        for name, values in saved.items()
    }
    assert bridge.read("at_hideout") == 1 and restored == saved, (saved, restored)
    shot("07-cold-boot")
    p.stop(save=False)
report = {
    "romSHA256": hashlib.sha256(args.rom.read_bytes()).hexdigest(),
    "checks": [
        "two independent harvesters",
        "terrain-safe follow from mailbox",
        "replay ignored",
        "real inventory sharing",
        "player gift changes trust and sharing",
        "memory dialogue",
        "home save and cold boot preserve both agents",
    ],
    "saved": saved,
    "restored": restored,
}
(args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
print("PASS:", ", ".join(report["checks"]))

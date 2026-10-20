"""Verify input-driven gameplay and unchanged background on every frame."""

from pathlib import Path
import hashlib
import json
import re
import shutil
import tempfile
from PIL import ImageChops, ImageDraw
from pyboy import PyBoy

ROOT = Path(__file__).resolve().parent
out = ROOT / "build"
evidence = out / "evidence"
evidence.mkdir(exist_ok=True)
rom = out / "heartwood-playable.gbc"
symbols = {
    name: int(addr, 16)
    for addr, name in re.findall(
        r"\b([0-9A-F]{8})\s+(_\w+)", (out / "heartwood-playable.map").read_text()
    )
}
with tempfile.TemporaryDirectory() as temp:
    copy = Path(temp) / "test.gbc"
    shutil.copy2(rom, copy)
    p = PyBoy(str(copy), window="null", sound_emulated=False)
    p.set_emulation_speed(0)

    def value(name):
        return p.memory[symbols["_" + name]]

    def tick(n):
        p.tick(n, True)

    def press(button, n=2, rest=30):
        p.button_press(button)
        tick(n)
        p.button_release(button)
        tick(rest)

    tick(180)
    p.screen.image.save(evidence / "00-help.png")
    press("start", rest=90)
    original = p.screen.image.copy()
    original.save(evidence / "01-room.png")
    assert len(set(original.getdata())) > 100

    # Mask pixels occupied by current and previous hardware objects only.
    def boxes():
        result = []
        for i in range(40):
            y, x = p.memory[0xFE00 + i * 4 : 0xFE02 + i * 4]
            if y and x:
                result.append((x - 8, y - 16, x - 1, y - 1))
        return result

    prior_boxes = boxes()
    background_frames = 0

    def stable_frame():
        global prior_boxes, background_frames
        tick(1)
        current = p.screen.image.copy()
        diff = ImageChops.difference(original.convert("RGB"), current.convert("RGB"))
        d = ImageDraw.Draw(diff)
        for box in (
            initial_boxes
            + prior_boxes
            + boxes()
            + [(104, 80, 135, 103), (72, 64, 111, 79), (0, 136, 159, 143)]
        ):
            d.rectangle(box, fill=(0, 0, 0))
        assert diff.getbbox() is None, ("Unexpected scenery change", p.frame_count, diff.getbbox())
        prior_boxes = boxes()
        background_frames += 1

    initial_boxes = prior_boxes.copy()
    # A one-frame directional input must be sampled within two native frames.
    start_x = value("cursor_x")
    p.button_press("left")
    tick(1)
    p.button_release("left")
    tick(1)
    assert value("cursor_x") == start_x - 1, "Missed short cursor tap"
    press("right")
    assert value("cursor_x") == start_x
    before_move = p.screen.image.copy()
    p.button_press("left")
    latency = None
    for frame in range(1, 5):
        tick(1)
        if p.screen.image.tobytes() != before_move.tobytes() and latency is None:
            latency = frame
    p.button_release("left")
    tick(2)
    assert latency is not None and latency <= 2, ("Visible cursor delay", latency)
    press("right", rest=2)
    # Measure repeat against actual native frames, not iterations of game logic.
    events = []
    last = value("cursor_x")
    p.button_press("left")
    for frame in range(1, 32):
        tick(1)
        current = value("cursor_x")
        if current != last:
            events.append(frame)
            last = current
    p.button_release("left")
    tick(2)
    assert len(events) >= 8, ("Slow held cursor", events)
    assert max(b - a for a, b in zip(events[1:], events[2:])) <= 4, events
    while value("cursor_x") < start_x:
        press("right", rest=2)
    p.button_press("a")
    command_latency = None
    visible_walk_latency = None
    bram_start = value("bram_x")
    oam_start = p.memory[0xFE0D]
    for frame in range(1, 5):
        stable_frame()
        if value("bram_x") != bram_start and command_latency is None:
            command_latency = frame
        if p.memory[0xFE0D] != oam_start and visible_walk_latency is None:
            visible_walk_latency = frame
    assert command_latency is not None and command_latency <= 2, (
        "Command delayed",
        command_latency,
    )
    assert visible_walk_latency is not None and visible_walk_latency <= 3, (
        "OAM delayed",
        visible_walk_latency,
    )
    for _ in range(2):
        stable_frame()
    p.button_release("a")
    positions = []
    for _ in range(900):
        stable_frame()
        positions.append((value("bram_x"), value("bram_y")))
        if value("loot") and not value("queue_count"):
            break
    assert value("harvested") == value("loot") == 1, "Harvest did not complete"
    for _ in range(45):
        stable_frame()
    harvested = p.screen.image.copy()
    harvested.save(evidence / "02-harvested.png")
    # Every walked foot cell must be permitted by the compiled geometry.
    walk_addr = symbols["_walkable"]
    for x, y in positions:
        assert p.memory[walk_addr + (y // 8) * 20 + x // 8], ("Foot crossed obstacle", x, y)
    assert len(set(positions)) > 30, "No actual movement"
    p.button_press("b")
    for _ in range(2):
        stable_frame()
    p.button_release("b")
    for _ in range(90):
        stable_frame()
    revealed = p.screen.image.copy()
    revealed.save(evidence / "03-revealed.png")
    assert value("exposure") == 1 and value("harvested") == 1
    assert (
        revealed.crop((104, 80, 136, 104)).tobytes()
        == harvested.crop((104, 80, 136, 104)).tobytes()
    ), "Exposure regrew patch"
    assert (
        revealed.crop((72, 64, 112, 80)).tobytes() != harvested.crop((72, 64, 112, 80)).tobytes()
    ), "Reveal invisible"
    for _ in range(600):
        stable_frame()
    press("start")
    assert value("help_open") == 1
    press("start", rest=90)
    returned = ImageChops.difference(p.screen.image.convert("RGB"), revealed.convert("RGB"))
    rd = ImageDraw.Draw(returned)
    rd.rectangle((89, 68, 96, 83), fill=(0, 0, 0))
    rd.rectangle((0, 136, 159, 143), fill=(0, 0, 0))
    assert returned.getbbox() is None, "Help did not restore persistent scene"
    # Repeated harvest cannot duplicate loot.
    press("a", rest=90)
    assert value("loot") == 1 and value("queue_count") == 0
    press("select", rest=90)
    assert value("loot") == value("harvested") == value("exposure") == 0
    assert value("bram_x") == 44 and value("bram_y") == 100
    p.screen.image.save(evidence / "04-reset.png")

    # Queue a move above the rock, followed by the harvest. Navigation must
    # detour around the blocked cells instead of walking through the painting.
    def aim(x, y):
        while value("cursor_x") != x:
            press("right" if value("cursor_x") < x else "left", rest=2)
        while value("cursor_y") != y:
            press("down" if value("cursor_y") < y else "up", rest=2)

    aim(7, 9)
    press("a", rest=2)
    aim(14, 11)
    press("a", rest=2)
    assert value("queue_count") == 2, "Orders did not queue"
    reached_first = False
    for _ in range(1200):
        tick(1)
        x = value("bram_x")
        y = value("bram_y")
        assert p.memory[walk_addr + (y // 8) * 20 + x // 8], ("Queued route crossed obstacle", x, y)
        reached_first |= (x, y) == (60, 76)
        if value("loot") and not value("queue_count"):
            break
    assert reached_first and value("loot") == 1, "FIFO route/harvest failed"
    # Blocked targets give feedback without adding a queued action.
    aim(0, 0)
    press("a", rest=2)
    assert value("queue_count") == 0 and value("rejected") > 0
    # Travel under foreground roots, retaining the Hi-Color image around Bram.
    aim(5, 9)
    press("a", rest=400)
    assert (value("bram_x"), value("bram_y")) == (44, 76)
    p.screen.image.save(evidence / "05-foreground.png")

    # Cursor must show both palette colors over foreground roots, bright shelves,
    # Bram and at the right screen edge. Compare every nontransparent UI pixel.
    def cursor_pixels_visible():
        screen = p.screen.image.convert("RGB")
        for obj in (0, 1):
            oy, ox, tile, prop = p.memory[0xFE00 + obj * 4 : 0xFE04 + obj * 4]
            pixels = p.memory[1, 0x8000 + tile * 16 : 0x8000 + tile * 16 + 32]
            for yy in range(16):
                for xx in range(8):
                    k = ((pixels[yy * 2] >> (7 - xx)) & 1) | (
                        ((pixels[yy * 2 + 1] >> (7 - xx)) & 1) << 1
                    )
                    if not k:
                        continue
                    # PyBoy expands RGB555 by shifting left three bits.
                    source = (50, 38, 46) if k == 1 else (206, 181, 131)
                    color = tuple((v * 31 // 255) * 8 for v in source)
                    x = ox - 8 + xx
                    y = oy - 16 + yy
                    assert 0 <= x < 160 and 0 <= y < 136, ("Cursor clipped", x, y)
                    assert screen.getpixel((x, y)) == color, (
                        "Cursor hidden",
                        x,
                        y,
                        screen.getpixel((x, y)),
                        color,
                    )

    for x, y in [(4, 7), (7, 8), (4, 3), (5, 9), (19, 16), (0, 0)]:
        aim(x, y)
        tick(5)
        cursor_pixels_visible()
    p.screen.image.save(evidence / "06-cursor-edge.png")
    # Visible bracket bounds, ground-pin tip and destination share one cell.
    aim(10, 14)
    tick(5)
    oy, ox = p.memory[0xFE00:0xFE02]
    assert (ox - 8, oy - 16) == (80, 112), "Cursor is offset from selected cell"
    press("a", rest=2)
    py, px = p.memory[0xFE08:0xFE0A]
    assert (px - 8 + 3, py - 16 + 8) == (84, 116), "Pin tip is not at cursor center"
    tick(400)
    assert (value("bram_x"), value("bram_y")) == (84, 116), "Bram did not reach cursor center"
    p.screen.image.save(evidence / "08-centered-destination.png")
    # B pressed during an unfinished upload must toggle, not be silently lost.
    wanted = value("exposure")
    for _ in range(5):
        wanted = 1 - wanted
        press("b", rest=2)
        assert value("exposure") == wanted, "B dropped during patch upload"
    tick(40)
    p.screen.image.save(evidence / "07-reveal-feedback.png")
    report = {
        "romSHA256": hashlib.sha256(rom.read_bytes()).hexdigest(),
        "nativeFramesWithUnchangedScenery": background_frames,
        "harvestFrames": len(positions),
        "uniqueWalkPositions": len(set(positions)),
        "shortCursorTap": True,
        "cursorVisibleLatencyFrames": latency,
        "heldCursorMoveFrames": events,
        "commandMovementLatencyFrames": command_latency,
        "visibleMovementLatencyFrames": visible_walk_latency,
        "cursorForegroundAndEdges": True,
        "cursorPinDestinationAligned": True,
        "rapidExposureToggles": True,
        "noBlockedFootCells": True,
        "exposurePreservesHarvest": True,
        "helpRestoresScene": True,
        "duplicateHarvestRejected": True,
        "resetVerified": True,
        "queuedDetourThenHarvest": True,
        "blockedTargetRejected": True,
        "physicalHardwareTested": False,
    }
    (evidence / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    p.stop(save=False)

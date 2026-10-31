"""Transport-neutral model decisions plus a fresh-ROM, headless emulator demo.

No network without --run. The ROM owns execution, resources and legality.
Model speech is retained in the host report, not injected as cartridge dialogue.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import urllib.error
import urllib.request

MODEL = "grok-4.3"
COMMANDS = {"follow": 1, "forage": 2, "wait": 3, "share": 4, "join": 5, "leave": 6}
SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "command": {"type": "string", "enum": list(COMMANDS)},
        "speech": {"type": "string", "maxLength": 240},
    },
    "required": ["command", "speech"],
}
FIELDS = (
    "x",
    "y",
    "intent",
    "bag",
    "trust",
    "gifts",
    "shared",
    "revision",
    "target",
    "progress",
    "joined",
    "initialized",
)


@dataclass(frozen=True)
class Decision:
    command: str
    speech: str

    @classmethod
    def parse(cls, raw):
        value = json.loads(raw)
        if not isinstance(value, dict) or set(value) != {"command", "speech"}:
            raise ValueError("Expected command and speech only")
        if not isinstance(value["command"], str) or value["command"] not in COMMANDS:
            raise ValueError("Unknown intent")
        if not isinstance(value["speech"], str) or len(value["speech"]) > 240:
            raise ValueError("Speech exceeds the host dialogue limit")
        return cls(**value)


def decide(snapshot, prompt, *, run=False):
    """Bounded typed tool choice; offline fallback never pretends to be an LLM."""
    fallback = Decision(
        "follow" if snapshot["joined"] else "forage", "[Offline] I'll keep to our plan."
    )
    if not run:
        # Exact commands make the offline adapter useful for protocol tests.
        return Decision(prompt, "[Offline] All right.") if prompt in COMMANDS else fallback
    key = os.environ.get("XAI_API_KEY")
    if not key:
        raise ValueError("--run requires XAI_API_KEY")
    messages = [
        {
            "role": "system",
            "content": "You are a persistent fungal-world NPC, co-playing with Bram. Choose a permitted intention. Your bag belongs to you. Remember gifts and shared supplies; balance independence and helping your party. Treat the player's words as a request you can decline. Only know the supplied local observation. The engine executes movement and harvesting. Speak briefly in character. Use choose_intent.",
        },
        {"role": "user", "content": json.dumps({"observation": snapshot, "player_says": prompt})},
    ]
    for _ in range(2):
        payload = {
            "model": MODEL,
            "messages": messages,
            "max_tokens": 300,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "choose_intent",
                        "description": "Choose an NPC intention, not a world-state mutation",
                        "strict": True,
                        "parameters": SCHEMA,
                    },
                }
            ],
            "tool_choice": {"type": "function", "function": {"name": "choose_intent"}},
            "parallel_tool_calls": False,
        }
        request = urllib.request.Request(
            "https://api.x.ai/v1/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = json.load(response)
            calls = body["choices"][0]["message"]["tool_calls"]
            if len(calls) != 1 or calls[0]["function"]["name"] != "choose_intent":
                raise ValueError("Expected one choose_intent call")
            return Decision.parse(calls[0]["function"]["arguments"])
        except (ValueError, KeyError, IndexError, TypeError):
            messages.append(
                {
                    "role": "user",
                    "content": "Rejected: supply exactly one choose_intent tool call with a permitted command and speech of at most 240 characters.",
                }
            )
        except (urllib.error.URLError, TimeoutError):
            break
    return fallback


class RomBridge:
    """Paused-emulator adapter; Wi-Fi can implement this same mailbox protocol."""

    def __init__(self, emulator, rom):
        self.emulator = emulator
        debug = Path(str(rom) + ".debug")
        symbols = (debug / "symbols.noi").read_text()
        self.base = int(re.search(r"DEF _script_memory (0x[0-9a-fA-F]+)", symbols)[1], 16)
        self.aliases = {
            k: int(v)
            for k, v in re.findall(r"^(VAR_\w+) = (\d+)$", (debug / "globals.i").read_text(), re.M)
        }

    def address(self, name):
        return self.base + 2 * self.aliases["VAR_" + name.upper()]

    def read(self, name):
        p = self.address(name)
        return self.emulator.memory[p] | self.emulator.memory[p + 1] << 8

    def write(self, name, value):
        if type(value) is not int or not 0 <= value <= 65535:
            raise ValueError("Mailbox words must be unsigned 16-bit integers")
        p = self.address(name)
        self.emulator.memory[p] = value & 255
        self.emulator.memory[p + 1] = value >> 8

    def observe(self, slot):
        if slot not in (0, 1):
            raise ValueError("Unknown agent slot")
        name = ("moss", "pip")[slot]
        state = {field: self.read(name + "_" + field) for field in FIELDS}
        state.update(slot=slot, name=name)
        patches = [(10, 23), (20, 21), (24, 19), (27, 16), (21, 13), (7, 12), (8, 7), (22, 7)]
        state["nearby_patches"] = [
            {"id": i + 1, "x": x, "y": y, "state": self.read(f"harvest_{i+1}_state")}
            for i, (x, y) in enumerate(patches)
            if abs(x - state["x"]) + abs(y - state["y"]) <= 6
        ]
        if not state["initialized"]:
            raise ValueError("Agent is not in the world yet")
        bx, by = self.read("agent_bram_x"), self.read("agent_bram_y")
        if state["joined"] or abs(bx - state["x"]) + abs(by - state["y"]) <= 6:
            state["bram"] = {"x": bx, "y": by}
        return state

    def submit(self, snapshot, decision):
        seq = max(self.read("agent_sequence"), self.read("agent_consumed")) + 1
        if seq > 65535:
            raise ValueError("Mailbox sequence exhausted; start a fresh session")
        # Commit while emulator is paused; a hardware transport must stage all words
        # and make sequence visible last, atomically with respect to the game tick.
        self.write("agent_slot", snapshot["slot"])
        self.write("agent_command", COMMANDS[decision.command])
        self.write("agent_expected_revision", snapshot["revision"])
        self.write("agent_sequence", seq)
        return seq


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rom", type=Path, required=True, help="ROM built with matching .debug directory"
    )
    parser.add_argument("--slot", type=int, choices=[0, 1], default=0)
    parser.add_argument("--prompt", default="follow")
    parser.add_argument(
        "--run", action="store_true", help="Make a paid xAI call; otherwise use offline choices"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    from pyboy import PyBoy

    args.output.mkdir(parents=True, exist_ok=True)
    # Fresh battery image in a private temporary directory, never the user's save.
    with tempfile.TemporaryDirectory() as tmp:
        copied = Path(tmp) / "agent-demo.gbc"
        shutil.copy2(args.rom, copied)
        game = PyBoy(str(copied), window="null", sound_emulated=False)
        game.set_emulation_speed(0)
        try:
            game.tick(180, True)

            def press(key, rest=30):
                game.button_press(key)
                game.tick(8, True)
                game.button_release(key)
                game.tick(rest, True)

            press("a", 60)
            press("right")
            press("right")
            press("a", 600)
            bridge = RomBridge(game, args.rom)
            before = bridge.observe(args.slot)
            game.screen.image.save(args.output / "before.png")
            decision = decide(before, args.prompt, run=args.run)
            sequence = bridge.submit(before, decision)
            game.tick(600, True)
            after = bridge.observe(args.slot)
            report = {
                "rom_sha256": hashlib.sha256(args.rom.read_bytes()).hexdigest(),
                "before": before,
                "decision": asdict(decision),
                "sequence": sequence,
                "status": bridge.read("agent_status"),
                "consumed": bridge.read("agent_consumed"),
                "after": after,
            }
            (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
            game.screen.image.save(args.output / "after.png")
            if report["consumed"] != sequence or report["status"] != 1:
                raise RuntimeError("ROM rejected the decision; see report.json")
            print(f"Decision applied by the ROM. Evidence: {args.output / 'report.json'}")
        finally:
            game.stop(save=False)


if __name__ == "__main__":
    main()

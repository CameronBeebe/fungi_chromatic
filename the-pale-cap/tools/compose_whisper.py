"""Original 4-channel hUGETracker v6 score: a slow call/answer over soft wave bass.
Binary layout follows GB Studio 4.3.2 saveUGESong. No sampled/copyrighted music.
"""

from pathlib import Path
import struct, math, json

P = Path(__file__).resolve().parents[1]
out = bytearray()


def u8(x):
    out.extend(struct.pack("<B", x))


def u32(x):
    out.extend(struct.pack("<I", x))


def string(s):
    b = s.encode("ascii")
    u8(len(b))
    out.extend(b.ljust(255, b"\0"))


def instrument(kind, index):
    u32(kind)
    string(
        ("Glass spores" if kind == 0 else "Root hum" if kind == 1 else "Silent air")
        if index == 0
        else ""
    )
    u32(0)
    u8(0)
    u8(4 if kind == 0 and index == 0 else 0)
    u32(1)
    u8(5 if kind == 0 else 0)  # quiet decay, no rising buzz
    u32(0)
    u32(0)
    u32(0)
    u8(2 if kind == 0 else 0)
    u32(3 if kind == 1 else 0)
    u32(0)
    u32(0)
    u8(0)
    for _ in range(64):
        u32(90)
        u32(0)
        u32(0)
        u32(0)
        u8(0)


u32(6)
string("A Grammar of Spores")
string("The Pale Cap")
string("Original ambient loop; E minor / C / G / D; quiet call and response.")
for kind in range(3):
    for index in range(15):
        instrument(kind, index)
for wave in range(16):
    for t in range(32):
        u8(round(7.5 + 7 * math.sin(t * 2 * math.pi / 32)) if wave == 0 else 8)
u32(10)
u8(0)
u32(0)
patterns = []
chords = [
    (4, [16, 23, 26, 30, 28, 23, 19, 14]),
    (0, [16, 19, 23, 26, 23, 19, 16, 12]),
    (7, [19, 23, 26, 31, 30, 26, 23, 19]),
    (2, [14, 21, 26, 28, 26, 21, 18, 14]),
]
for root, melody in chords:
    for channel in range(4):
        rows = [(90, 0, 0, 0) for _ in range(64)]
        if channel == 0:
            for i, n in enumerate(melody):
                rows[i * 8] = (n, 1, 0, 0)
        elif channel == 1:
            for i, n in enumerate(melody[::2]):
                rows[i * 16 + 6] = (n - 12, 1, 0, 0)
        elif channel == 2:
            # Eight slow steps per phrase, with a pickup into the next root.
            next_root = {4: 0, 0: 7, 7: 2, 2: 4}[root]
            third = 3 if root == 4 else 4
            bass = [
                root,
                root + 7,
                root + 12,
                root + third,
                root + 7,
                root + 12,
                root + 7,
                next_root + 12,
            ]
            for i, n in enumerate(bass):
                rows[i * 8] = (n, 1, 0, 0)
        patterns.append(rows)
u32(len(patterns))
for key, rows in enumerate(patterns):
    u32(key)
    for note, ins, fx, param in rows:
        u32(note)
        u32(ins)
        u32(0)
        u32(fx)
        u8(param)
for channel in range(4):
    u32(5)
    for bar in range(4):
        u32(bar * 4 + channel)
    u32(0)
for _ in range(16):
    u32(0)
(P / "assets/music/grammar-of-spores.uge").write_bytes(out)
(P / "assets/music/grammar-of-spores.uge.gbsres").write_text(
    json.dumps(
        {
            "_resourceType": "music",
            "id": "grammar-of-spores",
            "name": "A Grammar of Spores",
            "symbol": "music_grammar_of_spores",
            "filename": "grammar-of-spores.uge",
            "type": "uge",
            "settings": {},
        },
        indent=2,
    )
    + "\n"
)
print(len(out), "bytes; four 64-row phrases at 10 ticks/row (~43 sec loop)")

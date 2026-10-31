"""Shared Heartwood data for the cell-label calibration eval. No network.

The scene is the 160x144 decoded native image in examples/heartwood/source.png.
Jev's recorded cell probabilities are in examples/heartwood/labels.json: a 10x9
grid of 16 px cells named A1 (top left) to J9 (bottom right), letter = column.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "heartwood"
HERE = Path(__file__).resolve().parent

COLS, ROWS, CELL = 10, 9, 16
FOOT_COLS, FOOT_ROWS, FOOT = 20, 18, 8
LABELS = ["walkable", "fungus", "harvest_candidate", "water", "built_structure"]
WALK_FAIL = [
    "not_connected",
    "no_dwarf_display",
    "not_look_walkable",
    "cant_stand",
    "not_selectable",
]
CSV_FIELDS = ["cell_id", "row", "col"] + LABELS + ["walk_fail_" + r for r in WALK_FAIL] + ["notes"]
YES, NO = "yes", "no"
SKIP = {"", "skip"}


def cell_ids() -> list[str]:
    return [f"{chr(65 + x)}{y + 1}" for y in range(ROWS) for x in range(COLS)]


def cell_xy(cell_id: str) -> tuple[int, int]:
    """Zero-based (column, row) for a cell id such as 'C4'."""
    x, y = ord(cell_id[0]) - 65, int(cell_id[1:]) - 1
    if not (0 <= x < COLS and 0 <= y < ROWS):
        raise ValueError("Unknown cell id: " + cell_id)
    return x, y


def load_jev(path: Path | str = EXAMPLE / "labels.json") -> dict[str, dict[str, float]]:
    """Recorded Jev probabilities per cell and label. These are not human labels."""
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    out = {}
    for row in rows:
        probs = row["labels"]
        if set(probs) != set(LABELS):
            raise ValueError("Unexpected label set for " + row["id"])
        out[row["id"]] = {k: float(probs[k]) for k in LABELS}
    if sorted(out) != sorted(cell_ids()):
        raise ValueError("Expected exactly the 90 Heartwood cells")
    return out


def load_authored_walkable(path: Path | str = EXAMPLE / "candidate.json") -> dict[str, bool]:
    """Cameron's authored, playtested 20x18 foot grid, sampled at each 16 px cell center.

    A cell center (16x+8, 16y+8) falls in foot cell (2x+1, 2y+1). This is the authored
    grid, not a set of human labels made for this eval.
    """
    walk = json.loads(Path(path).read_text(encoding="utf-8"))["defaults"]["walkable"]
    if len(walk) != FOOT_COLS * FOOT_ROWS:
        raise ValueError("Unexpected authored grid size")
    out = {}
    for cid in cell_ids():
        x, y = cell_xy(cid)
        fx, fy = (CELL * x + CELL // 2) // FOOT, (CELL * y + CELL // 2) // FOOT
        out[cid] = bool(walk[fy * FOOT_COLS + fx])
    return out


def load_human(path: Path | str) -> dict[str, dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    out = {}
    for row in rows:
        cid = (row.get("cell_id") or "").strip().upper()
        cell_xy(cid)
        out[cid] = row
    return out


def blank_rows() -> list[dict[str, str]]:
    rows = []
    for cid in cell_ids():
        x, y = cell_xy(cid)
        row = {f: "" for f in CSV_FIELDS}
        row.update(cell_id=cid, row=str(y + 1), col=str(x + 1))
        rows.append(row)
    return rows


def write_rows(path: Path | str, rows: list[dict[str, str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({f: row.get(f, "") for f in CSV_FIELDS})


def neighbours(cid: str) -> list[str]:
    x, y = cell_xy(cid)
    out = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS:
            out.append(f"{chr(65 + nx)}{ny + 1}")
    return out


def walkable_components(walkable: set[str]) -> list[list[str]]:
    """4-connected components of the given cells, largest first, ties by grid order."""
    order = {c: i for i, c in enumerate(cell_ids())}
    seen, comps = set(), []
    for start in sorted(walkable, key=order.get):
        if start in seen:
            continue
        stack, comp = [start], []
        seen.add(start)
        while stack:
            c = stack.pop()
            comp.append(c)
            for n in neighbours(c):
                if n in walkable and n not in seen:
                    seen.add(n)
                    stack.append(n)
        comps.append(sorted(comp, key=order.get))
    comps.sort(key=lambda comp: (-len(comp), order[comp[0]]))
    return comps


def isolated_walkable(human: dict[str, dict[str, str]]) -> list[str]:
    """Cells labeled walkable that are not 4-connected to the largest walkable region."""
    walk = {c for c, r in human.items() if (r.get("walkable") or "").strip().lower() == YES}
    comps = walkable_components(walk)
    return [c for comp in comps[1:] for c in comp]

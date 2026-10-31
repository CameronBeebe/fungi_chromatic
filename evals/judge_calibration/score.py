"""Score Jev's recorded Heartwood cell labels against Cameron's hand labels.

Five separate yes/no tasks: walkable, fungus, harvest_candidate, water and
built_structure. Jev's probabilities come from examples/heartwood/labels.json
(recorded output, no API calls here). For each task: raw agreement, Cohen's kappa
with a bootstrap 95% interval, a confusion matrix, precision and recall for each
class, a threshold sweep, the Brier score and a calibration-by-bin table.

harvest_candidate is a design choice, not a fact about the pixels, so it is
reported as agreement with designer preference rather than accuracy.

The report also compares Jev walkable with the authored, playtested foot grid in
candidate.json. That grid is a baseline. It is not a set of human labels.

Optional drift check: --compare another_labels.json (same format as the recorded
Jev file) reports how often two judge runs on the same cells agree.

Usage, from the repo root:
    uv run --locked python -m evals.judge_calibration.score
    uv run --locked python -m evals.judge_calibration.score --labels path/to/labels.csv
"""

from __future__ import annotations

import argparse
import os
import random
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

from evals.judge_calibration import heartwood as hw

CLASSES = [hw.YES, hw.NO]
THRESHOLDS = [round(0.1 * i, 1) for i in range(1, 10)]
BINS = [(0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0)]
DEFAULT_LABELS = hw.HERE / "labels.csv"
DEFAULT_JEV = hw.EXAMPLE / "labels.json"
TITLES = {
    "walkable": "walkable",
    "fungus": "fungus",
    "harvest_candidate": "harvest_candidate (agreement with designer preference, not accuracy)",
    "water": "water",
    "built_structure": "built_structure",
}


# --- metrics (ported from the fungi_fortress judge-calibration scorer) ------


def confusion(
    human: Sequence[str], judge: Sequence[str], classes: Sequence[str]
) -> list[list[int]]:
    """Rows are human labels, columns are judge labels."""
    index = {c: i for i, c in enumerate(classes)}
    matrix = [[0] * len(classes) for _ in classes]
    for h, j in zip(human, judge):
        matrix[index[h]][index[j]] += 1
    return matrix


def agreement(human: Sequence[str], judge: Sequence[str]) -> float:
    if not human:
        return float("nan")
    return sum(h == j for h, j in zip(human, judge)) / len(human)


def cohens_kappa(human: Sequence[str], judge: Sequence[str], classes: Sequence[str]) -> float:
    n = len(human)
    if n == 0:
        return float("nan")
    po = agreement(human, judge)
    pe = sum((list(human).count(c) / n) * (list(judge).count(c) / n) for c in classes)
    if pe == 1.0:
        return 1.0 if po == 1.0 else 0.0
    return (po - pe) / (1 - pe)


def per_class(
    human: Sequence[str], judge: Sequence[str], classes: Sequence[str]
) -> dict[str, dict[str, Any]]:
    out = {}
    for c in classes:
        tp = sum(h == c and j == c for h, j in zip(human, judge))
        predicted = sum(j == c for j in judge)
        actual = sum(h == c for h in human)
        out[c] = {
            "precision": tp / predicted if predicted else None,
            "recall": tp / actual if actual else None,
            "support": actual,
            "predicted": predicted,
        }
    return out


def bootstrap_kappa(
    human: Sequence[str],
    judge: Sequence[str],
    classes: Sequence[str],
    reps: int = 2000,
    seed: int = 0,
) -> tuple[float, float]:
    """Percentile 95% interval. Fixed seed so the report is reproducible."""
    n = len(human)
    if n < 2:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    values = []
    for _ in range(reps):
        idx = [rng.randrange(n) for _ in range(n)]
        values.append(cohens_kappa([human[i] for i in idx], [judge[i] for i in idx], classes))
    values.sort()
    return values[int(0.025 * reps)], values[int(0.975 * reps) - 1]


# --- probability metrics ---------------------------------------------------


def to_label(p: float, threshold: float) -> str:
    return hw.YES if p >= threshold else hw.NO


def brier(human: Sequence[str], probs: Sequence[float]) -> float:
    if not human:
        return float("nan")
    return sum((p - (h == hw.YES)) ** 2 for h, p in zip(human, probs)) / len(human)


def calibration_bins(human: Sequence[str], probs: Sequence[float]) -> list[dict[str, Any]]:
    rows = []
    for lo, hi in BINS:
        idx = [i for i, p in enumerate(probs) if lo <= p < hi or (hi == 1.0 and p == 1.0)]
        rows.append(
            {
                "bin": f"{lo:.1f}-{hi:.1f}",
                "n": len(idx),
                "mean_p": sum(probs[i] for i in idx) / len(idx) if idx else None,
                "human_yes_rate": (
                    sum(human[i] == hw.YES for i in idx) / len(idx) if idx else None
                ),
            }
        )
    return rows


def sweep(human: Sequence[str], probs: Sequence[float]) -> list[dict[str, Any]]:
    rows = []
    for t in THRESHOLDS:
        judge = [to_label(p, t) for p in probs]
        yes = per_class(human, judge, CLASSES)[hw.YES]
        rows.append(
            {
                "threshold": t,
                "agreement": agreement(human, judge),
                "kappa": cohens_kappa(human, judge, CLASSES),
                "precision": yes["precision"],
                "recall": yes["recall"],
            }
        )
    return rows


# --- pairing ----------------------------------------------------------------


def paired(
    human_rows: dict[str, dict[str, str]], jev: dict[str, dict[str, float]], label: str
) -> dict[str, Any]:
    human, probs, ids, bad = [], [], [], []
    unlabeled = 0
    for cid in hw.cell_ids():
        row = human_rows.get(cid)
        value = ((row or {}).get(label) or "").strip().lower()
        if value in hw.SKIP:
            unlabeled += 1
            continue
        if value not in CLASSES:
            bad.append(f"{cid}={value}")
            continue
        human.append(value)
        probs.append(jev[cid][label])
        ids.append(cid)
    return {"human": human, "probs": probs, "ids": ids, "unlabeled": unlabeled, "bad": bad}


# --- report -----------------------------------------------------------------


def _fmt(x: Any) -> str:
    if x is None:
        return "n/a"
    if isinstance(x, float):
        return "n/a" if x != x else f"{x:.2f}"
    return str(x)


def binary_block(
    human: Sequence[str], judge: Sequence[str], ids: Sequence[str], ref: str, other: str
) -> list[str]:
    lo, hi = bootstrap_kappa(human, judge, CLASSES)
    lines = [
        f"- Raw agreement: {_fmt(agreement(human, judge))}",
        f"- Cohen's kappa: {_fmt(cohens_kappa(human, judge, CLASSES))} "
        f"(bootstrap 95% interval {_fmt(lo)} to {_fmt(hi)})",
        "",
        f"Confusion matrix (rows: {ref}, columns: {other})",
        "",
        f"| {ref} \\ {other} | " + " | ".join(CLASSES) + " |",
        "|---|" + "---|" * len(CLASSES),
    ]
    for c, row in zip(CLASSES, confusion(human, judge, CLASSES)):
        lines.append(f"| {c} | " + " | ".join(str(v) for v in row) + " |")
    lines += [
        "",
        f"| class | precision | recall | {ref} count | {other} count |",
        "|---|---|---|---|---|",
    ]
    for c, m in per_class(human, judge, CLASSES).items():
        lines.append(
            f"| {c} | {_fmt(m['precision'])} | {_fmt(m['recall'])} | "
            f"{m['support']} | {m['predicted']} |"
        )
    misses = [f"{i} ({ref} {a}, {other} {b})" for i, a, b in zip(ids, human, judge) if a != b]
    lines += ["", f"Disagreements: {', '.join(misses) if misses else 'none'}", ""]
    return lines


def label_section(label: str, p: dict[str, Any], threshold: float) -> list[str]:
    h, probs = p["human"], p["probs"]
    lines = [f"## {TITLES[label]}", ""]
    lines.append(
        f"Scored: {len(h)}. Unlabeled or skip: {p['unlabeled']}. Invalid: {len(p['bad'])}."
    )
    if p["bad"]:
        lines.append("Invalid labels: " + ", ".join(p["bad"]))
    lines.append("")
    if not h:
        return lines + ["Nothing to score yet.", ""]
    judge = [to_label(x, threshold) for x in probs]
    lines.append(f"Jev yes means probability >= {threshold:.2f}.")
    lines.append("")
    lines += binary_block(h, judge, p["ids"], "human", "jev")
    lines += [
        f"- Brier score: {_fmt(brier(h, probs))} (0 is perfect; always answering 0.5 gives 0.25)",
        "",
        "Threshold sweep",
        "",
        "| threshold | agreement | kappa | precision (yes) | recall (yes) |",
        "|---|---|---|---|---|",
    ]
    for r in sweep(h, probs):
        lines.append(
            f"| {r['threshold']:.1f} | {_fmt(r['agreement'])} | {_fmt(r['kappa'])} | "
            f"{_fmt(r['precision'])} | {_fmt(r['recall'])} |"
        )
    lines += [
        "",
        "Calibration by bin",
        "",
        "| Jev probability | cells | mean Jev probability | human yes rate |",
        "|---|---|---|---|",
    ]
    for r in calibration_bins(h, probs):
        lines.append(
            f"| {r['bin']} | {r['n']} | {_fmt(r['mean_p'])} | {_fmt(r['human_yes_rate'])} |"
        )
    return lines + [""]


def walk_reason_section(human_rows: dict[str, dict[str, str]]) -> list[str]:
    no_walk = [c for c, r in human_rows.items() if (r.get("walkable") or "").lower() == hw.NO]
    if not no_walk:
        return []
    lines = ["## Why cells are not walkable (human reasons)", ""]
    lines.append(f"Cells labeled not walkable: {len(no_walk)}.")
    lines.append("")
    for reason in hw.WALK_FAIL:
        n = sum((human_rows[c].get("walk_fail_" + reason) or "").lower() == hw.YES for c in no_walk)
        lines.append(f"- {reason}: {n}")
    return lines + [""]


def connectivity_section(human_rows: dict[str, dict[str, str]]) -> list[str]:
    isolated = hw.isolated_walkable(human_rows)
    if not isolated:
        return []
    return [
        "## Connectivity check",
        "",
        "These cells are labeled walkable but are not connected (4-way) to the largest "
        "walkable region, so they fail condition (a) of the walkable definition. "
        "Relabel them or explain in notes: " + ", ".join(isolated),
        "",
    ]


def authored_section(
    jev: dict[str, dict[str, float]],
    authored: dict[str, bool],
    threshold: float,
    human_rows: dict[str, dict[str, str]],
) -> list[str]:
    ids = hw.cell_ids()
    ref = [hw.YES if authored[c] else hw.NO for c in ids]
    judge = [to_label(jev[c]["walkable"], threshold) for c in ids]
    lines = [
        "## Baseline: Jev walkable vs the authored grid (not human labels)",
        "",
        "The authored grid is Cameron's playtested 20x18 foot grid from "
        "examples/heartwood/candidate.json, sampled at each cell center. It marks the route "
        "the prototype actually uses, so it is stricter than Jev's question, which asks only "
        "whether the spot could hold a walker's feet. It is not a set of hand labels for this eval.",
        "",
        "Row 9 cell centres sit under the bottom 8 px HUD, where the authored grid has no foot "
        "positions, so row 9 disagreements are expected.",
        "",
    ]
    lines += binary_block(ref, judge, ids, "authored", "jev")
    p = paired(human_rows, jev, "walkable")
    if p["human"]:
        h_by = dict(zip(p["ids"], p["human"]))
        hids = [c for c in ids if c in h_by]
        lines += [
            "### Human walkable vs the authored grid",
            "",
            "How closely the new hand labels match the authored grid. Not a judge score.",
            "",
        ]
        lines += binary_block(
            [h_by[c] for c in hids],
            [hw.YES if authored[c] else hw.NO for c in hids],
            hids,
            "human",
            "authored",
        )
    return lines


def drift_section(
    a: dict[str, dict[str, float]], b: dict[str, dict[str, float]], name_b: str, threshold: float
) -> list[str]:
    lines = [
        f"## Drift: recorded Jev vs {name_b}",
        "",
        "Judge against judge on the same cells. No human labels involved.",
        "",
    ]
    for label in hw.LABELS:
        ids = [c for c in hw.cell_ids() if c in a and c in b]
        la = [to_label(a[c][label], threshold) for c in ids]
        lb = [to_label(b[c][label], threshold) for c in ids]
        flipped = [c for c, x, y in zip(ids, la, lb) if x != y]
        mean_abs = sum(abs(a[c][label] - b[c][label]) for c in ids) / len(ids) if ids else None
        lines.append(
            f"- {label}: {len(ids)} shared, agreement {_fmt(agreement(la, lb))}, "
            f"kappa {_fmt(cohens_kappa(la, lb, CLASSES))}, mean probability change "
            f"{_fmt(mean_abs)}, changed: {', '.join(flipped) or 'none'}"
        )
    return lines + [""]


def build_report(
    labels_path: str | os.PathLike | None = DEFAULT_LABELS,
    jev_path: str | os.PathLike = DEFAULT_JEV,
    candidate_path: str | os.PathLike = hw.EXAMPLE / "candidate.json",
    compare_path: str | os.PathLike | None = None,
    threshold: float = 0.5,
) -> str:
    jev = hw.load_jev(jev_path)
    authored = hw.load_authored_walkable(candidate_path)
    have_labels = labels_path is not None and Path(labels_path).exists()
    human_rows = hw.load_human(labels_path) if have_labels else {}
    labeled = sum(
        any((r.get(k) or "").strip().lower() in CLASSES for k in hw.LABELS)
        for r in human_rows.values()
    )
    lines = [
        "# Heartwood cell-label calibration report",
        "",
        "- Scene: Heartwood only (one 160x144 scene, 90 cells of 16x16 px).",
        f"- Jev probabilities: `{Path(jev_path).name}` (recorded output; this script makes no API calls).",
        f"- Human labels: `{Path(labels_path).name if have_labels else 'none'}`, "
        f"{labeled} of 90 cells labeled.",
        "",
        "Human labels are the reference. Precision is the share of Jev's yes (or no) calls the "
        "human agreed with; recall is the share of the human's yes (or no) labels Jev also gave. "
        "One scene is a small sample, so read the intervals, not just the point values.",
        "",
    ]
    if not labeled:
        lines += [
            "Labels pending: no human labels yet, so only the authored-grid baseline is shown.",
            "",
        ]
    else:
        lines += connectivity_section(human_rows)
        for label in hw.LABELS:
            lines += label_section(label, paired(human_rows, jev, label), threshold)
        lines += walk_reason_section(human_rows)
    lines += authored_section(jev, authored, threshold, human_rows)
    if compare_path:
        lines += drift_section(jev, hw.load_jev(compare_path), Path(compare_path).name, threshold)
    return "\n".join(lines).rstrip() + "\n"


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Score recorded Jev cell labels against hand labels."
    )
    parser.add_argument("--labels", default=str(DEFAULT_LABELS), help="human labels CSV")
    parser.add_argument("--jev", default=str(DEFAULT_JEV), help="recorded Jev probabilities")
    parser.add_argument("--candidate", default=str(hw.EXAMPLE / "candidate.json"))
    parser.add_argument("--compare", default=None, help="second Jev probabilities file for drift")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--out", default=None, help="also write the report to this path")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if not 0.0 < args.threshold < 1.0:
        parser.error("--threshold must be between 0 and 1")
    report = build_report(args.labels, args.jev, args.candidate, args.compare, args.threshold)
    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())

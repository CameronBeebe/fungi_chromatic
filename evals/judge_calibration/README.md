# Heartwood cell-label calibration

How well do Jev's cell labels match a human's? This eval compares Jev's recorded
probabilities for the Heartwood scene with hand labels from the designer.

Status: one scene (Heartwood, 90 cells). **Human labels are pending.** Until
`labels.csv` exists, the report shows only the authored-grid baseline below.
Nothing here calls an API. Expanding to the other five 160x144 scenes in
`the-pale-cap/assets/backgrounds/` would need new, approved live Jev runs.

## What is being judged

`the-pale-cap/tools/jev_scene_inspect.py` asked Jev five independent yes/no
questions about the exact center of each 16x16 cell of the decoded 160x144 image
(10x9 grid, A1 top left to J9 bottom right). The answers are recorded in
`examples/heartwood/labels.json`. Each label is scored as its own yes/no task.

| label | meaning for the human label |
|---|---|
| walkable | see the definition below |
| fungus | fungal growth is visible at the center (cap, stalk, gills, shelf fungus, mycelium) |
| harvest_candidate | the designer would want this to be a small collectable resource |
| water | exposed water at the center, not water hidden under a bridge deck |
| built_structure | something constructed at the center (boards, deck, steps, masonry, furniture) |

harvest_candidate is a design preference, not a fact about the pixels, so the
report calls it "agreement with designer preference", not accuracy.

### Walkable

A cell counts as walkable only if ALL of these hold:

- (a) it is connected to the main walkable region, not an isolated patch in a random spot;
- (b) a dwarf can be displayed there;
- (c) it looks walkable in the image;
- (d) a walker could stand there;
- (e) it can be selected as a tile the dwarf can move to.

This is stricter than the question Jev was asked, which was about local foot
support only ("Judge local support separately from whether there is a connected
route here"). Expect disagreement from that difference alone; the optional reason
boxes show which condition failed. Row 9 cell centers sit under the bottom 8 px HUD.

## Label

From the repo root:

```sh
uv run --locked python -m evals.judge_calibration.label_server
```

Then open <http://127.0.0.1:8765/>. The page runs locally only and saves to
`evals/judge_calibration/labels.csv`. It never shows Jev's answers.

- Arrow keys move, or click a cell. `1`-`5` toggle the five labels.
- `Q W E R T` toggle the reasons walkable failed: not connected, no dwarf display,
  doesn't look walkable, can't stand, not selectable.
- `Enter` marks the cell done, saves and moves on. `K` skips a cell. `N` adds a note.
- `G` toggles the grid. `O` toggles the authored walk grid from `candidate.json` as
  a reference. It is off by default so it doesn't anchor your labels.
- Cells labeled walkable but not connected (4-way) to the largest walkable region
  are outlined in orange, as a reminder of condition (a).
- Untouched cells stay blank in the CSV and are left out of scoring, not counted as no.
- "Download CSV" exports the same file if saving to disk fails.

`labels_template.csv` shows the columns: cell id, row, col, the five labels
(`yes`, `no`, `skip` or blank), the five `walk_fail_*` reasons and notes.

## Score

```sh
uv run --locked python -m evals.judge_calibration.score --out evals/judge_calibration/report.md
```

For each label: raw agreement, Cohen's kappa with a bootstrap 95% interval,
confusion matrix, precision and recall for yes and for no, the list of
disagreeing cells, a threshold sweep from 0.1 to 0.9, the Brier score and a
calibration-by-bin table (Jev probability against the human yes rate). Jev "yes"
means probability >= 0.5 unless `--threshold` says otherwise. The report also
counts walkable failure reasons and repeats the connectivity check.

`--compare other.json` adds a drift check between the recorded Jev file and a
second run in the same format. It compares judge with judge; no human labels.

### Baseline: the authored grid (not human labels)

`examples/heartwood/candidate.json` holds the playtested 20x18 foot grid the
Heartwood prototype uses. Sampled at each cell center and compared with Jev
walkable at 0.5, it gives agreement 0.63 and kappa 0.34 (bootstrap 95% interval
0.22 to 0.48). Jev marked all 21 authored walkable cells as walkable but also 33
cells the authored grid leaves out, 9 of them in the HUD row. That grid is the
route the prototype actually uses, so it is a useful baseline, but it is not the
hand labeling this eval asks for. Once labels exist the report also shows how
the human labels compare with it.

## Limits

- One scene and 90 cells. Intervals will be wide; treat results as a first look.
- Jev's answers are a single recorded run. Repeat runs need approved API use.
- Cells are 16x16 proposals, not pixel masks or collision.

## Tests

```sh
uv run --locked python scripts/test.py
```

The eval tests use synthetic labels only, marked as such. They check the metrics
against hand-worked examples, the authored-grid baseline, the connectivity
helper, the local server and save path, and key safety: the scorer runs with API
keys unset, synthetic canary values placed in the environment never reach any
output, outputs are scanned for anything key-like, and the eval code contains no
network client or key reads.

# Jev scene classification probe

Offline experiment for proposing terrain labels and object bounds from our scene
art. It never writes collision, sprite, background or ROM files. The source art
and generated report remain local and ignored under `build/`.

## Run

Use Python with Pillow installed (the existing Chromatic PyBoy environment has
it). Set `TYPESAFE_API_KEY` in the environment; never put credentials in arguments
or checked-in files. There is no SDK installation and no credential in saved
requests or reports.

From the repository root:

```sh
python3 the-pale-cap/tools/jev_scene_probe.py path/to/scene.png
python3 the-pale-cap/tools/jev_scene_probe.py path/to/scene.png --run --resume
python3 the-pale-cap/tools/jev_scene_probe.py path/to/scene.png \
  --focus-cells H3,I4,C2,E7,D4 --run --resume
python3 the-pale-cap/tools/jev_scene_probe.py path/to/scene.png \
  --focus-cells H3,I4,C2,E7,D4,H6 --interactions --run --resume
```

Without `--run`, this prepares images and the request only. `--resume` also lets
you regenerate the report from matching saved responses without any API call.
It fingerprints the actual images, prompt and explicit model, excluding random
image placeholder IDs. Changed input cannot silently reuse an earlier response.
No automatic retries or fallback models are used.

`--run` sends the selected images and questions to TypeSafe and incurs usage.
Default model: `jev-1.14.0`, with experimental image support explicitly enabled.
The initial pass asks 90 terrain questions over a labeled 10x9 grid and presence
plus bounding-box questions for three objects. Override objects with repeated
`--target` arguments. `--cols` and `--rows` control grid resolution. Native 160x144
art is enlarged to 480x432 with nearest-neighbor scaling to meet image API limits.
The close-up variant supplies additional crops around explicitly selected cells.
It sends the full clean image AND labeled full-image grid AND local crops together.
Cells run from A1 at top left to J9 at bottom right in the default grid.

`--interactions` adds an independent category question per selected cell: harvest,
mine, container, entrance/exit, talk, none or unclear. Terrain and interaction are
separate: a solid object may be a harvest target. These are visually suggested
affordances, not facts about implemented mechanics. The Interactions view is
available for runs that asked those questions. Each question selects a primary
category; multiple simultaneous interaction tags are a possible later extension.

Open `build/index.html` in the built-in browser using a local server. It contains
all retained runs, terrain overlays, adjustable candidate-ground threshold,
object boxes and per-cell probabilities. The candidate-ground threshold is a
review heuristic, not measured collision accuracy. Object boxes appear only when
the separate presence question is at least 75%; a box alone is not evidence an
object exists. Hover cells or box edges for details. Raw answers and request
images are saved alongside the report for inspection.

## First live results — October 14, 2026

Four successful requests to `jev-1.14.0`:

- Heartwood generated master (`heartwood-playable/build/master-full.png`):
  90 cells + six object questions; 22,581 input tokens; 1.170 seconds.
- Chalk ordinary concept (`concept-art/overworld-study-v2-2026-10-11/candidates/C2-O-160x144.png`):
  90 cells + six object questions; 22,578 input tokens; 1.117 seconds.
- Heartwood five-cell close-up follow-up: 4,434 input tokens; 1.085 seconds.
- Heartwood six-cell close-ups with independent interaction categories:
  6,815 input tokens; 1.176 seconds. H6 (the small mushroom patch) was harvest
  with 96% probability, E7 (open ground) was none with 94%, and I4 (water) was
  none with 86%. D4 (a root/shelf region) was harvest with 97% despite not being
  an authored harvest target: a useful warning against equating appearance with
  game rules. The script was not given the authored interaction map.

The grid-only prompt was too permissive: 73/90 Heartwood and 80/90 Chalk cells
had ground as their top label. These counts do not mean the cells are walkable.
On Heartwood, explicit close-ups changed H3 from ground to water (water probability
19% → 81%) and I4 from ground to water (14% → 86%). C2 became more clearly solid
(48% → 91%); E7 remained ground (93% → 100%). D4 switched from ground to solid
but remained ambiguous (56% solid versus 43% ground). These are targeted examples
chosen after inspecting failures, not an independent accuracy benchmark.

All calls together used 56,408 input tokens. Durations measure local HTTP request
time including network; this tiny sample is not a latency benchmark. A cache-only
rerun reused saved answers without a key or network request. No production assets
or game mechanics changed.

## Interpretation and next test

Jev looks useful for provisional labels, particularly with local crops and global
context together. A single full-scene grid query is not reliable enough here.
Next: annotate a held-out set of cell centers ourselves, test crop prompts on that
set, then measure false walkable labels, uncertainty and connectivity. Review
height, steps, overhangs, character clearance and reachable interaction positions
separately. An apparently clear surface may still be unreachable. Keep uncertain
cells out of automatic navigation; never accept a coarse label as a pixel mask.

## Jev as scene author — October 14

The newer [scene-generation direction](../../SCENE-GENERATION.md) lets Jev choose
meaning within a bounded game vocabulary. Classification confidence is retained
for review; it is not an accuracy threshold for the authoring compiler. This is
a different policy from the adjustable ground-candidate threshold in the probe UI.

```sh
python3 the-pale-cap/tools/jev_scene_package.py \
  the-pale-cap/art-tests/heartwood-playable/build/master-decoded.png --run
python3 the-pale-cap/tools/test_jev_scene_package.py
```

This pass uses the independently decoded Hi-Color image, not the preconversion
painting used by the first four requests above. It supplies the full image, grid
and ten explicit crops per call, across nine calls. Cached rows are reused without
an API key or `--run`. The current 136px visible-height contract excludes foot
positions hidden by the bottom eight-pixel HUD; `--visible-height` is explicit.

Output lives in ignored `build/package/<revision>/`: source image, frozen
interpretation, scene JSON and review page. Candidate fields cover region labels,
bounded harvest sites, reachable approach cells, finite action templates, stable
IDs, initial state and local art-state jobs. Source hashes, prompt fingerprints
and explicit model versions bind the package to its inputs. Region adjacency
does not imply individual object identity: the harvest template proposes one-cell
sampling sites within a broader colony, rather than deleting the entire region.

The live decoded-image pass used 94,627 input tokens across nine requests totaling
6.772 seconds of HTTP time. It proposed 24 harvesting sites in one region; six have
reachable work positions. Code tests cover bounded patches, unreachable targets,
deterministic revisions, HUD exclusion and a serialized depleted site yielding
nothing on a second harvest. This is a candidate manifest, not a new playable ROM.
Its art-state jobs are requests only; no new pixels, patterns or game assets are
written. Actor clearance, height, exits, native integration and hardware checks
remain explicit promotion blockers.

## References

- [Release](https://typesafe.ai/blog/jev-1-14)
- [Images and image limits](https://docs.typesafe.ai/images)
- [Box output](https://docs.typesafe.ai/primitives/box)
- [Choice output](https://docs.typesafe.ai/primitives/choice)
- [Models and pricing](https://docs.typesafe.ai/models)

No third-party source is vendored. Pillow is an existing optional tool dependency;
networking uses Python's standard library. TypeSafe is an external service, not a
cartridge runtime dependency.

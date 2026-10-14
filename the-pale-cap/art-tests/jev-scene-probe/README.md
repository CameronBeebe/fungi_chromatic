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

## Proposal → Jev → Inspect

```sh
python3 the-pale-cap/tools/jev_scene_inspect.py \
  the-pale-cap/art-tests/heartwood-playable/build/master-decoded.png --run
python3 -m unittest discover -s the-pale-cap/tools -p 'test_jev_scene*.py'
```

Requires `XAI_API_KEY` and `TYPESAFE_API_KEY` for uncached calls; Pillow remains the
only non-standard-library dependency. Keys are read at request time and never
written to the requests, results or browser page. `--run` sends the selected art
and prompts to xAI and TypeSafe. No key or `--run` is needed for a cached replay.
No automatic retries or fallback models are used. `--proposer-model` explicitly
selects a compatible xAI model; the default is `grok-4.3`, verified available on
the development account. Record the returned model too, since provider aliases
can evolve. This prototype uses the documented Chat Completions JSON-schema API;
it does not install an SDK or invoke model tools.

The proposer sees the clean decoded scene plus a grid, enlarged with nearest
neighbor. It proposes up to twelve objects, short Inspect descriptions, approximate
anchor cells and overlapping descriptive tags. Jev separately judges object
presence, full-image bounds, prose fit, unsupported mechanical promises and each
tag. Nine other requests independently label every cell's center for walkability,
fungus, harvest suitability, exposed water and built structure. Those cell calls
do not see the proposal text. No automatic fungus-to-harvest rule is applied.

The browser study has clickable Inspect targets, a 0–100% display threshold,
optional labeled grid and per-cell scores, and an option to reveal rejected
proposals. Hover highlights a cell and shows all five probabilities; click pins
the readout across layer/cutoff changes. Arrow keys select cells, Enter pins and
Escape releases. A compact sticky readout keeps scores visible on narrow screens.
The cutoff filters only the current label overlay, never the frozen scene rules. Accepted descriptions must
pass the explicitly recorded provisional policy. A proposed anchor more than one
cell outside Jev's box is held for review: the models may mean different instances.
This is disagreement detection, not accurate segmentation. Small boxes are selected
above larger overlapping boxes; names also provide keyboard-accessible selection.
Gameplay actions other than browser Inspect remain disabled. Navigation heatmaps
show local support, not collision, and exclude the HUD-covered bottom-row foot
positions. Bridge connectivity and elevation transitions still need validation.

The first live run produced eight proposals and five accepted Inspect descriptions.
Two were held for visual/prose fit; one mushroom had an anchor/box disagreement.
For boardwalk cell H2, the independent walkable and built-structure probabilities
were 0.76 and 0.95. This is an illustrative result, not an accuracy benchmark.
The run made one xAI call and eleven Jev calls, totaling 24.784 seconds of HTTP time;
Jev used 90,220 input tokens. Exact usage and timing are in `evidence.json`.

Outputs are ignored under `build/inspect/<revision>/`: `scene.json`, `evidence.json`,
`source.png`, and `index.html`. Requests/responses are fingerprinted under
`build/inspect/requests/`; the source image is snapshotted once. Scene identity
includes labels, copy, policy, source hash and request/model provenance, excluding
variable HTTP timing. The compiled interpretation is frozen for the revision.
`build/inspect/index.html` points to the latest run. The root report and movement
package link to this study, and the study links back to both.

Tests cover overlapping labels, no harvest inference from fungi alone, absent
objects, contradictory/promise-laden prose, spatial disagreement, invalid inputs,
model versions, cached replay, frozen identity and safe HTML embedding. Original
ROM/art files are unchanged. A production text-length/font pass is still needed.

## References

- [Release](https://typesafe.ai/blog/jev-1-14)
- [Images and image limits](https://docs.typesafe.ai/images)
- [Box output](https://docs.typesafe.ai/primitives/box)
- [Choice output](https://docs.typesafe.ai/primitives/choice)
- [Independent yes/no labels](https://docs.typesafe.ai/primitives/noul)
- [xAI image inputs](https://docs.x.ai/developers/model-capabilities/images/understanding)
- [xAI structured output](https://docs.x.ai/developers/model-capabilities/text/structured-outputs)
- [Models and pricing](https://docs.typesafe.ai/models)

No third-party source is vendored. Pillow is an existing optional tool dependency;
networking uses Python's standard library. TypeSafe and xAI are external services, not
cartridge runtime dependencies.

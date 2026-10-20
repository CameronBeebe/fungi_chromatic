> Historical notes. Current behavior is documented in the root README and current design/specifications.

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
Default model: the pinned Jev model, with experimental image support explicitly enabled.
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

Four successful requests to the pinned Jev model:

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

The newer [scene-generation direction](../../the-pale-cap/SCENE-GENERATION.md) lets Jev choose
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
optional grid lines and an option to reveal rejected proposals. Cell IDs and
percentages are not painted over the scene; probabilities appear on hover.
Estimated object bounds are hidden by default and shown only for the selected
object when explicitly enabled, with an explanation that they are not collision
or interaction hitboxes. Hover highlights a cell and shows all five probabilities; an explicit Pin readout button holds
the scores across layer/cutoff changes; ordinary clicks do not stop hover updates. Arrow keys select cells, Enter pins and
Escape releases. One full probability breakdown sits directly below the image, matching the
original probe interaction without painting text onto the scene.
The cutoff filters only the current label overlay, never the frozen scene rules. Accepted descriptions must
pass the explicitly recorded provisional policy. A proposed anchor more than one
cell outside Jev's box is held for review: the models may mean different instances.
This is disagreement detection, not accurate segmentation. Object names provide keyboard-accessible Inspect selection; diagnostic boxes
do not intercept cell-hover or pinning input.
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

## Supplying the art brief alongside the image

```sh
python3 the-pale-cap/tools/jev_scene_inspect.py \
  the-pale-cap/art-tests/heartwood-playable/build/master-decoded.png \
  --brief the-pale-cap/art-tests/jev-scene-probe/heartwood-art-context.txt --run
```

The optional brief is UTF-8 text, at most 16 KiB. Both proposal and object-review
requests carry it as intent, not proof of visible content. Object results record a
separate `briefAlignment` probability, which does not enable Inspect or override
presence. Image-only cell requests stay identical and reuse their caches. The
brief's bytes are hashed and its text is frozen in `scene.json`, saved separately
as `art-brief.txt`, and shown in the UI under “What this study does.” Changes to the
brief invalidate affected request caches and scene identity. No brief preserves
the earlier requests. The included example explicitly distinguishes Heartwood's
recorded clean-plate prompt from later additions in the native build.

The first brief-aware Heartwood run produced eight proposals, six accepted and
two held for review. The nine cell-label responses were reused unchanged. One
new proposal request and two object-review requests took 14.798 seconds of HTTP
time; the recorded full dependency timing is 21.425 seconds including the reused
cell requests. This is a changed interpretation, not evidence of improved accuracy.
The full brief-aware result was replayed with both API keys removed. Twenty-one
offline tests pass, including brief cache invalidation, input limits, provenance
freezing and high intent alignment never overriding low visual presence.

## Relationship and native state-change review

After creating the brief-aware Inspect study and the existing Heartwood harness
build, run this from the repository root with Pillow available:

```sh
python3 the-pale-cap/tools/jev_scene_review.py \
  the-pale-cap/art-tests/jev-scene-probe/build/inspect/6fe17560a504c3c0 \
  --plan the-pale-cap/art-tests/jev-scene-probe/heartwood-relations.json --run
```

The plan pins an Inspect revision and six candidate pairs. It is not portable to
another regenerated interpretation without reviewing and updating those IDs.
Use `--native-build PATH` for the matching existing harness build. The decoder
reads `master.til`, `.map`, `.atr`, `.pal` and the three resource arrays in
`assets.h`; it does not execute or rebuild that source. A fresh checkout requires
the locally preserved art input and prior build/Inspect outputs described above.
Do not replace a missing input with a lookalike: source hash and pixel matching
are checked before any calls. No new third-party code or package is required.

Two successful Jev requests test seven endpoint presences, six relations and
five before/after questions. Full decoded scenes and local crops are supplied;
no source painting or runtime sprite is included. The review uses integer nearest
enlargements with each dimension at least 384. A smaller batch with 256/288-pixel
crops was rejected as “Invalid image dimensions” despite the documented minima;
the exact cause within that batch is not isolated. No automatic retries or model
fallbacks are used. The two successful calls recorded 8,898 input tokens, 346
output tokens and 1.051 seconds total HTTP time; these are measurements of one
run, not a performance guarantee.

The dashboard is written under `build/review/<revision>/`. The report server's
`/review/` entry links to the latest result. It includes:

- Before / After / Compare wipe / Changed pixels, with native RGB hover readout.
- Aligned crops and optional authored edit boundary, without text over the art.
- Exact patch footprint, pixel counts, byte budget and input fingerprints.
- Each visual judgment separately, with the actual question and review flags.
- Selectable relationship pairs, probability filtering and optional estimated
  bounds. The connecting line is not a navigable path or an inferred physical strand.
- Frozen JSON, raw answers, usage and links back to the source Inspect review.

The first patch changed 280 pixels, none outside its 32x24 footprint; 12 patterns
use 192 patch bytes with unchanged map/attributes/palettes. Jev supported shelf/root
attachment at .92 and hypha/root attachment at .79. Four other relations remain
held, including unresolved endpoints. Harvest readability scored .85 but intact
fans only .42 and ground coherence .67, so the visual change also remains held
under provisional .70 review gates. These are useful disagreements, not proof
the asset is bad or the model is right. No scene actions or navigation are enabled.

The complete review replays with both API keys removed when `--run` is omitted.
Cache identity covers images, state, question wording and model; plan/review
policy changes are frozen into result identity. Old results are retained. Reports
and request caches stay ignored; only the tools, template and explicit plan are
versioned. Existing assets and native ROM remain untouched.

Run the offline invariants with:

```sh
python3 -m unittest discover -s the-pale-cap/tools -p 'test_jev_scene*.py'
```

33 tests cover prior package/Inspect behavior plus exterior changes, empty patches,
tile aliases, master mismatch, palette decoding, invalid arrays, relation direction,
duplicate/stale endpoints, unresolved-target gates, comparison cache identity,
independent review gates and safe HTML. The newer controls and prototype adapter
extend this coverage (53 scene tests total); human calibration and broader sprite
readability checks remain TODOs.

Browser checks covered the wipe/diff views, edit-boundary toggle, pixel RGB
readout, relationship selection, estimated bounds, probability filtering and
the empty-results state. The wipe starts over the edited area rather than the
unchanged center of the scene.

## Bounded controls and localization

```sh
python3 the-pale-cap/tools/jev_scene_controls.py \
  the-pale-cap/art-tests/jev-scene-probe/build/review/3c673440792143ec --run
```

Omit `--run` to replay cached evidence without a key or network. A frozen plan
compares two question versions on forward, identical-intact, identical-depleted
and reverse pairs. Expected answers stay outside model input. The existing
forward call is reused; at most nine new calls cover the other comparisons and
two location attempts. No retry-until-pass loop is used.

Both versions matched all four expected bands on this one scene. Full-image and
guided-crop boxes still disagree: zero mutual overlap. The controls dashboard
compares them with the original proposal and known patch footprint, preserving
that uncertainty. Outputs live under `build/controls/<revision>/` and can be
viewed through the existing report server's `/controls/` entry.

The [review-to-ROM editor](../../the-pale-cap/art-tests/scene-prototype/README.md) connects this frozen
evidence to corrected navigation and a bounded harvest contract. It builds a
separate native prototype after explicit review; API results cannot directly
inject commands, replace engine rules or imply human acceptance.

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

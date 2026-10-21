# Development-time scene pipeline

Working research tools for interpreting decoded native art, reviewing gameplay
data and building a bounded standalone prototype. No model calls run on the
cartridge. **The integrated GB Studio game does not consume these outputs yet.**

## Stages

1. `tools/jev_scene_probe.py`: classify terrain in full images and local cells.
2. `tools/jev_scene_package.py`: freeze candidate map evidence and expose a
   dashboard for navigation/threshold review.
3. `tools/jev_scene_inspect.py`: grok-4.3 proposes objects and descriptions from
   creative intent plus native pixels; Jev judges overlapping labels and bounds.
4. `tools/jev_scene_review.py`: inspect object relationships and before/after
   changes alongside exact pixel/patch checks.
5. `tools/jev_scene_controls.py`: compare forward, identical and reversed image
   pairs; preserve disagreements between whole-image and cropped localization.
6. [Review-to-ROM adapter](../scene-prototype/README.md): edit walkable cells,
   spawn/work positions and a harvest economy, approve, compile and emulator-test
   a separate Heartwood ROM. One fixed room/patch is supported today.

Each Python tool has `--help`. Run `uv sync --locked` from the repository root,
then invoke tools with `uv run --locked python`. The pinned Jev model is
centralized in [`pipeline_models.py`](../../tools/pipeline_models.py).

## Calls, caches and review

Live API requests require explicit `--run`. Credentials stay in environment
variables `TYPESAFE_API_KEY` and `XAI_API_KEY`; do not put them in files or browser
pages. Without `--run`, tools replay available cache entries or report missing
evidence. Build/review can run offline once its inputs exist. CI never makes
paid calls.

The API receives decoded native-resolution imagery, enlarged by integer nearest
neighbor where needed for image limits, plus whole-scene and aligned local views.
Jev's image support is explicitly enabled through its required request header.
Independent labels can overlap; they are not one mutually exclusive distribution.
Bounds and model probabilities are evidence, not proof of clearance or a runtime
permission to harvest. Deterministic code owns supported effects and budgets.

Local dashboards expose hover scores, probability filters, bounds, relationships,
exact diffs and before/after views. Human corrections are essential. Original
and stricter change questions passed four control pairs on one scene, while two
new mushroom-location boxes had no overlap. This is a diagnostic, not a general
accuracy claim. Automation fixtures are not human-approved scene packages.

Inputs/results, request caches and generated players live in ignored `build/`.
Recreating the initial model runs requires local original concept art and the
native [Heartwood harness](../heartwood-playable/README.md). A selected
[offline example](../../../examples/heartwood/README.md) ships the already encoded
art and recorded evidence for the review-to-ROM loop; it does not rerun generation. No concept image is silently uploaded without an explicit live run.

See [scene architecture](../../SCENE-GENERATION.md) and the
[historical experiment notes](../../../docs/notes/scene-pipeline-experiments.md)
for detailed commands, schemas and recorded evidence. `make test` runs the offline
invariant suite together with native save and inventory tests.

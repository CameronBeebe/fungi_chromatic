# Offline Heartwood example

Selected inputs for the experimental human-review-to-ROM adapter. These files
let a new clone inspect recorded model evidence and compile one playable room
without access to the local concept portfolio, API accounts or Codex tooling.
Use the [walkthrough](../../docs/GETTING_STARTED.md).

- `art/`: native tile patterns, map, attributes, palette schedule and the small
  C/header payload needed for the fixed harvest patch. These are intentional
  distribution inputs even though the original conversion generated them.
- `source.png`: the decoded native artwork shown to the models/reviewer.
- `labels.json`: recorded overlapping cell probabilities, not fresh inference.
- `review-evidence.json` and `control-evidence.json`: recorded object/relationship
  and before/after evidence, including disagreement. No raw request cache,
  credential, personal workstation path or private prompt is included.
- `candidate.json`: the original candidate's hashes, default settings and
  provenance. It is a seed, not a new human approval or a complete engine copy.

Frozen from candidate `4bf3215496093388`, review `3c673440792143ec`, inspect
`6fe17560a504c3c0`, and controls `4e3839fccc866d55`. The selected imagery is
original project artwork; the broad concept portfolio remains ignored.

`scene_prototype.py example` verifies the seed and files, snapshots the current
checked-in native engine, and derives a candidate identity that includes the
seed revision and current engine hashes. It writes only beneath the ignored
scene-prototype `build/` tree. Existing modified snapshots are rejected, not
replaced. There are no bundled ROMs or duplicate engine sources here.

The example is one fixed room, a 32×24 harvest patch, and simple supply/loot
counters. It does not demonstrate arbitrary scene generation, integrated game
levels, saves, extraction or hardware timing. Original material uses the root
[MIT license](../../LICENSE); reused renderer/player components retain their
[third-party terms](../../THIRD_PARTY_NOTICES.md).

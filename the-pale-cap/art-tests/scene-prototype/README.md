# Human review → playable ROM

This first adapter turns the existing Heartwood scene and review evidence into
editable gameplay settings, then a real standalone Game Boy Color ROM. It is a
mechanics iteration tool, not the integrated game's replacement.

The local editor supports painting walkable cells, choosing Bram's spawn and work
position, and changing harvest time, supply cost, starting supplies and loot yield.
Hover shows overlapping Jev probabilities below the art. A Jev walkability
proposal is available as a starting point; the playtested authored mask is the
default. Neither model bounds nor probabilities silently become collision.

## Run

For the self-contained offline example, install [uv](https://docs.astral.sh/uv/getting-started/installation/)
and run from the repository root:

```sh
uv sync --locked
uv run --locked python the-pale-cap/tools/scene_prototype.py example --serve
```

Viewing/editing needs no GBDK, API keys, local concept portfolio or plugin.
To build, install GBDK 4.5.0, set `GBDK_PATH`, then use:

```sh
uv sync --locked --extra demo
uv run --locked --extra demo python the-pale-cap/tools/scene_prototype.py example --verify --serve
```

The [walkthrough](../../../docs/GETTING_STARTED.md) covers setup and controls.
The [example](../../../examples/heartwood/README.md) contains selected encoded
art and recorded evidence; current engine code is snapshotted at preparation.
For a new locally generated review, use `prepare REVIEW_DIRECTORY --controls
CONTROLS_DIRECTORY`, then `verify CANDIDATE_DIRECTORY` and `serve
CANDIDATE_DIRECTORY`, with the same `uv run --locked --extra demo python
the-pale-cap/tools/scene_prototype.py` prefix. These upstream inputs remain local.

`serve` prints a loopback-only URL with an unguessable session path. Open it in the
browser. Review geometry and mechanics, check both review confirmations,
then **Approve & build prototype**. Edits clear those confirmations. The server
revalidates everything and records the exact reviewed specification. Compilation
and emulator tests run automatically; only a passing build gets playable/download
links. This never flashes a cartridge or replaces an existing game ROM.

`verify` makes a separately labeled **automation fixture**, not human approval.
It is useful for testing the pipeline before reviewing a scene. The editor links
the default fixture so a reviewer can immediately play the actual native ROM.

## What is frozen and checked

- Candidate identity covers the source review, optional control report, encoded
  art, engine snapshots and default settings. Snapshot changes invalidate builds.
- A build identity covers the candidate, reviewed settings, approval kind,
  builder/contract source and compiler executable. The rest of the installed
  toolchain is not vendored or fully fingerprinted; this is not a hermetic build.
- Walkable space must be one connected component, with reachable spawn/work
  cells, no walkable HUD/resource cells, and a work position touching the patch.
- 2–120 walkable cells bound the quadratic route table within its 16 KiB bank.
  Work time is 1–240 ticks; yield is 1–99; cost/supplies are 0–99.
- The compiler checks the native header and a 64 KiB ROM ceiling. PyBoy drives
  the actual ROM and checks movement, timing, cost/reward, repeat-harvest rejection,
  state across the help menu, and reset. An unaffordable configuration is allowed
  intentionally and tested for rejection rather than silently rebalanced.
- Outputs include the reviewed JSON, approval record, compiler diagnostics,
  manifest, ROM, real emulator before/after images and verification evidence.

The browser sends data only to its local server. API keys never enter it. POSTs
require the session path, same-origin header, bounded JSON and explicit review
flags. The server compiles a fixed source adapter; model output cannot supply
commands or executable code.

## Current limits and evidence

One fixed Heartwood room and one 32×24 harvest artwork patch are supported.
Geometry review still owns visual clearance, elevation and occlusion. The schema
does not invent state-change art for a new object. Supply and loot are prototype
counters; hideout, extraction, saving and multiple resource types are next steps.
The B action remains the explicitly labeled reveal test.

Three 64 KiB automation builds passed: default 60-tick work/+2 loot/1 supply;
alternate spawn with 120-tick work/+7 loot/2 supplies; and an unaffordable order.
Browser checks cover live numeric validation, Jev proposal, blocked-spawn
rejection and undo. These are emulator checks, not new physical-device tests.

All generated candidates, request data, ROMs and evidence live under ignored
`build/`. Keep original art and the previous ROM intact. Rendering and the browser
player reuse the existing Hi-Color and Binjgb components; see
[`THIRD_PARTY_NOTICES.md`](../../../THIRD_PARTY_NOTICES.md). No new third-party
code is introduced by this adapter.

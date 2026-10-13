# Playable Heartwood Hi-Color experiment

An isolated, input-driven GBDK ROM on top of the detailed Heartwood clean plate.
It preserves the production game, the designer's modular candidate and the local
concept portfolio. It is a rendering/gameplay feasibility test, not the next
production game build or approved character/resource artwork.

## Try it

- Start / Enter: enter the room or open help (pauses work; shows bag/queue counts).
- D-pad / arrows: move the designation cursor. First press is immediate; held
  directions repeat after eight ticks and then every four, following the
  production cursor's timing model.
- A / Z: enqueue walking to ground or harvesting the three small fans in the
  clearing to the right. Bram walks independently. Up to eight orders fit.
- B / X: toggle a small hyphal reveal above the patch. Harvested stays harvested.
- Select / Shift: reset this experiment, including the resource and bag.

The cursor begins over the resource. Press A to see the complete first interaction.
Blocked/full/duplicate requests briefly tint the cursor red. The current order
gets a small marker. No game saves, extraction, enemies, sound or networking.
The upper bridge/exits are scenery in this bounded clearing test.

## Build, validate, preview

From the repository root, using Python with Pillow and PyBoy installed:

```sh
python3 the-pale-cap/art-tests/heartwood-playable/build.py
python3 the-pale-cap/art-tests/heartwood-playable/verify.py
python3 the-pale-cap/art-tests/heartwood-playable/preview.py
```

The build uses `GBDK_PATH` / `--gbdk`, defaulting to the installed Chromatic
toolchain. `--source PATH` overrides the locally preserved 160x144 clean plate:
`concept-art/heartwood-assets-candidate-v1/source/layout-reference-160x144.png`.
That portfolio is ignored and is deliberately not uploaded. A fresh checkout
needs the local input. Original source SHA-256:
`0af7209d40f49d48b4f6fcecb58439295c446116700529283c1eb390b5a2b72e`.

All generated assets, ROM, hashes and evidence stay in ignored `build/`.
The preview serves the exact ROM using the existing GB Studio/Binjgb snapshot
from the Hearth study. It does not modify or rebuild the main GB Studio game.
It prints a new localhost URL. `--prepare-only` refreshes its files without
starting a server; an already-open player retains its loaded ROM until reload.

## What this proves

One 11,120-byte Hi-Color master retains the detailed source ground. One fixed
palette schedule serves all physical/perception states. The resource has a
192-byte pattern patch per state; the reveal has a 160-byte patch per state.
Pattern IDs are not deduplicated, so a tile update cannot alter another location.
The master occupies VRAM bank 0 tiles 0–255 and bank 1 tiles 0–103. Sprites occupy
bank 1 tiles 128–195, with no overlap. Maps remain in their separate VRAM areas.
The resulting padded ROM is 64 KiB; generated manifest records its exact hash.

Bram's eight native 16x16 frames use two overlaid object palettes, shared plum
shadows and ochre/ivory highlights. Four 8x16 objects form Bram, two form the
cursor and one marks the current order: at most seven per scanline in this test.
Some root-fringe tiles have foreground priority to overlap his upper body.
The character and fans are new studies, not production replacements.

Resource updates transfer one tile per refresh, over at most twelve updates.
This bounds upload work before the long palette ISR. The patch can therefore
change progressively over a short interval; it is not an atomic whole-patch
swap. Palette timing is reused from `../hearth-hicolor/src/gbc_hicolor.c`.

The isolated FIFO and incremental breadth-first search preserve the cursor/order
model. Production `ff_controls.c` depends on GB Studio VM/actors and routes for
the old map, so it is referenced for behavior rather than copied into this ROM.
Do not interpret this harness as production-engine integration.

## Validation and remaining work

The verifier boots the real ROM, designates work via buttons, checks all walked
foot cells, queues a detour before harvesting, rejects blocked targets/duplicate
harvests, switches exposure, round-trips through help and resets. It compares
963 consecutive native frames outside actual OAM rectangles and registered
patch areas: no unrelated scenery changes. It also checks a one-frame cursor
tap, persistent cut remains across exposure, and one item earned.

Collision is a hand-authored foot-position grid for this clearing, not a complete
actor-footprint or level annotation system. Music, more actors, queue UI,
larger worlds and production scheduling need separate budget/integration tests.
The reveal is deliberately subtle under the fixed master palettes. B requests
during an unfinished patch upload are ignored. Physical hardware testing and
art-direction approval are pending; the preceding static gallery's hardware
approval does not cover this executable.

## Provenance

The original generated clean-plate provenance is in the local designer handoff.
New sprite cells, resource shapes and build/gameplay code are authored here.
No new third-party package or renderer copy is vendored. The shared Hi-Color
renderer retains its upstream licensing clarification requirement, documented
in the Hearth study and root `THIRD_PARTY_NOTICES.md`; this experiment does not
resolve release licensing. The preview retains the existing Binjgb MIT files.

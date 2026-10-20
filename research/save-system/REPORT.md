# Save-system research

The historical investigation is in
[docs/notes/save-system-research.md](../../docs/notes/save-system-research.md).
It analyzes GBVM snapshot saves and early proposals, not the current game save ABI.

The implemented system uses two alternating semantic records and saves only at
home. See [game behavior](../../the-pale-cap/README.md),
[design rules](../../the-pale-cap/DESIGN.md), and the actual implementation in
[`ff_home_save.c`](../../the-pale-cap/plugins/colony-controls/engine/src/ff_home_save.c).
`make test` runs host-side interruption, corruption and fallback checks.

The JSON files here are historical measurements, not fresh build results.
`inspect_build.py` requires the named older local ROMs/debug symbols plus
`GB_STUDIO_ROOT` pointing to a matching GB Studio source checkout. They are not
required to build or test the current game.

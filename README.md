# Fungi Fortress

The game for the ModRetro Chromatic.

World seeds are grown in the Python lab, [fungi_fortress](https://github.com/CameronBeebe/fungi_fortress). This repo is the cartridge: maps, characters, and the ROM that gets flashed.

## Playable prototype

[The Pale Cap](the-pale-cap/README.md) is the editable Game Boy Color prototype.
Open `the-pale-cap/project.gbsproj` in GB Studio. It includes cursor-directed
orders, autonomous gathering, mycelial spells, animated color art and music.

The current slice includes an illustrated hideout, departure and queued return,
Luma's authored Gillsong gift, inspection and equipment, bag/stash transfers,
and versioned hideout-only saves. A valid save boots directly into the hideout.
Gillsong's gameplay ability, hideout construction, turn-based combat, spectrum
items, generated content and link trading remain planned work.

See the [design](the-pale-cap/DESIGN.md), [backlog](the-pale-cap/TODO.md),
[expedition specification](the-pale-cap/EXPEDITION-SLICE.md), and
[playtest evidence](the-pale-cap/PLAYTEST.md).

## Art exploration

The concept portfolio remains local in the ignored `concept-art/` directory;
it is not included in this checkpoint. The selected 160×144 Hearth source needed
for rebuilding is preserved in `the-pale-cap/art/source/`. [ART-PIPELINE.md](the-pale-cap/ART-PIPELINE.md) describes
conversion, palette constraints and seam diagnostics. The separate
[Hi-Color Hearth study](the-pale-cap/art-tests/hearth-hicolor/README.md) compares
scanline palettes with standard GBC rendering. The main game now uses its richer
104-pixel-high room above the functional home menu. Full-screen menus and other
scenes use normal engine rendering. Existing source assets remain preserved.

## Dependencies and licensing

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for GB Studio/GBVM,
GBDK, Hi-Color tooling and browser emulator provenance. Build tools are installed
externally; this repository does not vendor a complete development toolchain.
The existing `the-pale-cap/LICENSE` is the GB Studio MIT notice and must be
preserved. It does not by itself establish a license for all original game code
and art; a project-wide license has not yet been selected.

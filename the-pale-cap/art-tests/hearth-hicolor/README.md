# Root Hearth Hi-Color study

Standalone GBC rendering experiment, separate from the main game. It uses the
preserved source `the-pale-cap/art/source/root-hearth-160x144.png`.
No production background is replaced and no game save is read or written.

## Build and view

Set `GBDK_PATH` to an installed GBDK-2020 directory, then run `sh build.sh` from
this directory. The script requires GBDK_PATH and reports missing tools before building.
It invokes `png2hicolorgb` and `lcc`; prepared standard tiles, font and cropped
source are checked in. Build output: `bin/hearth-hicolor.gbc`.
The build also updates `web/rom/hearth-hicolor.gbc` for the included Binjgb
player. From the repository root, serve it with `uv run --locked python -m
http.server 8000 --bind 127.0.0.1 --directory the-pale-cap/art-tests/hearth-hicolor/web`
and open `http://127.0.0.1:8000/`. No plugin or developer code is needed.

- A/Z: Hi-Color; B/X: standard palettes; Select: toggle rendering.
- Start/Enter: open or close the menu study.
- Left/right: select BAG / HOME / EXIT. A/B closes the menu.

These menu entries are layout/input demonstrations, not functional inventory,
travel or extraction actions. Browser arrows control this demo only.

## Cost and evidence

Full image payload: 5,760 tile bytes, 360 map bytes, 360 attribute bytes and
4,640 palette bytes: **11,120 bytes**. The 104-pixel-high image above the menu
uses **8,040 bytes**. The standard comparison uses **6,544 bytes**. The 64 KiB
ROM includes both modes, menu data, code and bank padding.

Native emulator checks displayed the full Hi-Color and standard modes, opened
the cropped menu, moved its selection, and observed stable menu frames.
The full Hi-Color framebuffer contained 572 distinct colors. A browser preview
also displayed the study. No physical Chromatic test or CPU benchmark is claimed.
Hi-Color occupies much of the visible frame with palette updates; integration
must check input, audio, sprite timing and engine interrupt interactions.

## Provenance

`src/gbc_hicolor.c` and `.h` derive from the GBDK-2020 4.5.0 `examples/gb/hicolor`
renderer; its palette ISR is credited to Toxa. Local changes add menu palette
restoration after the shortened picture. The upstream `TODO: Permissive License`
header is retained for provenance. The upstream GBDK example source, including
these renderer files, is covered by the explicit CC0 notice also shipped as
`LICENSE_png2hicolorgb`; see the pinned source links and preserved notice in
the repository's [third-party notices](../../../THIRD_PARTY_NOTICES.md).
The upstream example illustration is not used here.

# Concept to cartridge artwork

The Root Hearth v1 exposed a conversion failure: independently picking the best
palette for each 8×8 tile creates visible rectangles on continuous surfaces.
Hardware constraints shape the artwork, but tile boundaries should not look like
arbitrary changes in lighting. Increasing palette variety alone does not solve it.

## Production stages

1. Preserve the concept and choose the exact screen composition. Identify player
   targets and the area the menu covers before drawing detail.
2. Author a native 160×144 master. Build clear silhouettes, value masses and pixel
   clusters. Keep the room, stash, threshold, preparation objects and effects in
   editable layers or separate sources. A reduced concept is only a layout guide.
3. Establish shared palette families by material and lighting. Share shadow and
   transition colors wherever continuous surfaces meet. Reserve the UI palette.
   Review and freeze approved palettes; do not relearn them on every art edit.
4. Convert with spatial continuity constraints. `tools/convert_background.py`
   is the current offline prototype: globally learned families, neighboring tile
   residual penalties, optional pixel cleanup, palette freezing and RGB555 output.
   It generates separate candidates and never writes production assets.
5. Review at native size and enlarged with nearest-neighbor scaling. Redraw weak
   clusters and object silhouettes in the master. Check tile-boundary artifacts,
   foreground noise, illumination and each interactive target's readability.
6. Audit real tile bytes, attributes, palettes, unique tiles and scene reservations.
   Independently decode exported data and compare it to the review image. A legal
   image still requires artistic review.
7. After approving that individual asset, register the native PNG, sidecar and
   palettes, build the cartridge and inspect actual emulator frames with menus.
   Hardware review remains a separate acceptance step.

## Animation

Plan palette cycling in the master using spatially ordered color indices. Keep
the animated material's palette separate from static text and framing. Use tile
frames for shape changes. Neither automatic quantization nor generic hue cycling
will reliably produce purposeful animation. Gillsong's cyan ornament is the first
integrated example; the Hearth needs authored flame/light regions before cycling.

## Current review

See `art-tests/root-hearth-conversion/README.md` and `comparison.png`. The revised
Hearth conversion is a more coherent draft and is not integrated. It still needs
deliberate native pixel reconstruction, especially the threshold and root texture.
The original concept, current background and current preview remain available.

## Project-local extension

`../skills/chromatic-art-pipeline/SKILL.md` packages this workflow alongside the
installed Chromatic plugin. It is versioned skill source in this repository,
not an alteration of the plugin cache or a global skill installation. A future
session can read that path directly. The plugin remains the native integration,
build and emulator layer.

The converter now accepts `--regions CONFIG`: native-pixel polygons lock covered
tiles to a common palette family. A region can learn its ramp collectively or
declare four explicit colors. Frozen reviewed palettes stay fixed unless an
explicit color override is supplied. Region coverage is visible in a tile map.

`tools/audit_background_seams.py` compares the source and candidate along tile
borders, marks extra contrast and emits ranked edge data. Use it to find review
areas; do not use its aggregate count as an artistic acceptance gate. Deliberate
quantized lighting steps can be flagged too.

The Root Hearth floor-region experiments remove independent palette changes
below the chest, but trade away some floor shading. They still need pixel-cluster
authoring and boundary review. Current game assets remain intact.

## Rendering beyond fixed background palettes

The four-colors-per-8×8 rule describes a tile with an unchanged palette. Changing
palette values between scanlines allows different rows of that tile to use
different actual colors. It does not change the tile's two-bit pixel indices.
GBDK's png2hicolorgb converter and example implement a richer-background route:
https://github.com/bbbbbr/png2hicolorgb
https://gbdk.org/docs/api/docs_toolchain_settings.html

Evaluate three separately labeled versions of the same Hearth composition:
authored standard background; standard background plus sprite highlights and
interactive objects; isolated scanline-palette/Hi-Color rendering study. Preserve
concepts and current assets until the individual candidate is chosen. Additional
colors do not automatically improve composition or repair poorly drawn clusters.

Hi-Color is particularly worth evaluating for static hideout and inspection
screens. The existing GB Studio LCD interrupt routines manage window visibility,
sprite hiding and background tile addressing. A scene-specific renderer must
coordinate or temporarily replace those routines and restore them on exit. The
bottom home menu, text palette, fades, music and save/navigation behavior need
explicit tests. High-color output carries CPU/ROM and timing costs; a desktop
reconstruction alone does not verify a functioning raster renderer.

Sprites can supply independent palettes and moving details over the room. Their
OAM and scanline budgets must be checked in the actual composition, especially
if combined with raster palette updates. Keep exploration separate from the
real-time overworld until menu transitions and physical Chromatic output pass.

## Integrated Hearth renderer — October 11

The main game uses the reviewed cropped Hi-Color image at home. Its 260 tiles
are repacked into 128 bank-0 tiles and 132 bank-1 tiles, leaving the engine's
font/UI tile ranges intact. `tools/prepare_hearth_hicolor.py` validates and
packages the checked-in converter outputs; the runtime does no image quantization.
The 8,040-byte payload stays in ROM and its active tiles/maps load into VRAM.

`ff_hearth.c` takes ownership of the LCD handler only while the room is visible.
It restores the UI palette during the last image row's HBlank. Full-screen menus,
inspection and departure relinquish that handler under black. Ordinary palettes
are revealed only after the full-screen menu or destination is ready. The home
scene disables its old automatic/explicit fade-in, which exposed the fallback
image before the Hi-Color upload. VRAM preparation keeps the LCD on and palettes
black, avoiding an LCD-off white flash.

The scene references `hearth-renderer-backing.png`, a uniform image that compiles
to one blank tile and the engine-required maps. It does not load a second Hearth
illustration. The original `root-hearth.png` remains an unreferenced source asset
and is absent from the linked ROM; the regression checks its symbols are absent.
The game remains locked by its ordinary home event; inventory/save mutations
continue through the existing tested code.

Because the palette loop masks interrupts across the image, home rendering clocks
the existing music routine after the last image row with a fractional accumulator preserving
the 256 Hz logical cadence (4389/1024 ticks per frame). This is appropriate for
the current non-streaming soundtrack; it is not support for streamed sound effects
or link transfers while the image renderer is active. Normal menus and other
scenes retain the engine timer. Emulator checks cover cadence and non-silent
output, not subjective sound quality or physical-device timing.

Do not move that music callback back into VBlank: a busy update can delay the
LYC 152 palette preload until scanline 153 and corrupt an occasional image frame.
The callback runs after the assembly renderer restores its real stack and ROM
bank. Regression coverage includes 3,600 consecutive room frames with music and
frame-by-frame entry, departure, menu-return, extraction and cold-boot checks.

# Gillsong — ornament and color refinement

Standalone rendering study. Its Vermilion art and ornament animation are now used by integrated item inspection; this ROM itself contains no inventory or item mechanics.

## Look first

- `comparison.png`: labeled, static before / Vermilion / Saffron / Rose, enlarged 3× with nearest-neighbor scaling. All use direct RGB555 expansion, so the comparison does not mix display treatments.
- `01-vermilion.png`, `02-saffron.png`, `03-rose.png`: exact 160×144 source reconstructions. Corresponding `-4x.png` files enlarge without smoothing.
- `gillsong-refinement.gbc`: 32 KiB GBC-only standalone test ROM.
- `emulator-evidence/01-boot-vermilion.png`, `03-saffron.png`, `04-rose.png`: actual native-resolution PyBoy framebuffers.
- `emulator-evidence/ornament-flow.gif`: 192 consecutive actual emulator frames; `animation-contact-sheet.png` gives labeled static samples. GIF timing is approximate; native timing is defined in `main.c`.

**Recommendation: Vermilion.** Brighter orange-red gills and creamy rims retain the lacquered fungus identity, with cyan-green ornament against a near-black violet field. Saffron is a warmer mineral alternative; Rose explores cooler plum and coral. These are art directions, not item variants or stats. “Gillsong,” “Amber,” and “Worn” remain presentation candidates.

## What changed

The fan-shaped fork is not redrawn or re-sampled: 105 fork-bearing tiles preserve their original two-bit pixel indices and palette assignments exactly. The retained baseline header is in `reference/`. New authored corner knots, coiled hyphal rosettes, branching stems, a double text-panel rule and separated label compartments replace the sparse frame and muddy lower-corner ornament. The six material palettes have carefully chosen alternatives; the remaining two separate animated cyan detail from stable UI and framing.

Animation follows spatially ordered color-index bands along the ornament's roots, middle and tips. A brief light passage lasts about 0.8 seconds, followed by about 2.4 seconds of rest. This uses Ferrari's principle of arranging indexed pixels for motion, rather than rotating the hue of the image. The fork and its gills remain static. Three shared bands mean separate curls move together; this is a small ornament experiment, not independently timed light along every filament. A still boot and exact B reset prevent animation from concealing the underlying art.

## Controls

- Right or Select: next palette; Left: previous palette. Wraps through three choices and returns to still mode.
- A: start/restart ornament flow.
- B: restore the exact static palette for the current choice.

## Verified

GBDK 4.5.0 compiled the ROM. PyBoy 2.7.0 ran that ROM, booted, exercised forward/backward wrap, Select, A and B, and retained real screenshots. Static output remained identical for 60 frames; B restored the exact boot framebuffer and stayed still for another 60. All 192 animation frames were checked: only 245 pixels changed, all in ornament palette 6. All 23,040 pixels of each of the three emulator stills match the decoded tile/palette data under PyBoy's channel expansion.

Normal GBC baseline: 160×144, 206 unique 8×8 tiles (original: 186), 3,296 tile bytes in VRAM bank 0, 360 tile-map bytes, 360 attribute bytes, eight four-entry background palettes per variation, maximum four colors per tile. No sprites and no raster palette switching. RGB555 entries are explicitly stored as 15-bit values. `audit.json` retains palettes, tile preservation and authored path data; `native-verification.json` independently checks the encoded assets; `emulator-evidence/verification.json` includes the tested ROM SHA-256 and control results. ROM header and global checksums passed. The build log contains one nonfatal optimizer warning.

## Display treatment and limits

Source PNGs expand each stored five-bit channel with `round(value × 255 / 31)`. This PyBoy build displays `value × 8`, verified against every framebuffer pixel, so its maximum is 248 instead of 255. A browser emulator may apply a different color transform. No browser appearance was measured here, and neither treatment establishes the physical Chromatic's brightness, gamut or contrast. Physical compatibility, display appearance and animation cadence remain untested; no hardware claim is made.

No Hi-Color build is included. More palettes per scanline would require a separate timing-sensitive raster implementation, sacrificing CPU time and demanding additional emulator and physical-device testing. It would not improve this baseline's native spatial resolution. The normal-color study is complete independently of that optional investigation.

## Reproduce

Run `sh reproduce.sh` from this directory. It regenerates PNGs, comparison, `art.h` and audit, compiles the ROM, runs controller tests and checks encoded pixels. Dependencies: Node plus Sharp, GBDK 4.5.0, Python with PyBoy 2.7.0 and Pillow. Set `GBDK_PATH`; optionally override `SHARP_MODULE` and `PYBOY_PYTHON`. Install Sharp through npm or provide its module path. All outputs stay here. The retained source header makes rebuilding independent of changes to the original directory.

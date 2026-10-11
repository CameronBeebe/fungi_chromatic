# Gillsong native screen study

Standalone art experiment. Does not replace game assets or implement item mechanics.

`gillsong-normal.gbc` is a built 32 KiB GBC-only ROM. `screen.png` is the exact 160×144 palette-constrained reconstruction; `screen-5x.png` enlarges those pixels without smoothing. Source illustration: portfolio sheet 14. UI text was rebuilt at native resolution.

## Validation

- 186 unique background tiles, eight palettes, maximum four colors per tile.
- Palette entries quantized to RGB555. Native graphics analysis passed.
- ROM built successfully and displayed in the native emulator.
- A enables palette cycling on the small cyan tracery at the left; B restores the static palette. Both inputs exercised, followed by neutral input. Recording retained in `emulator-evidence`.
- The illustrated fork itself is static in this baseline. This is not a Hi-Color raster implementation.
- Not yet tested on the physical Chromatic; not flashed to the cartridge.

## Next visual experiments

- Design color-index bands into gills and hyphae so cycling conveys traveling light rather than indiscriminate hue rotation.
- Compare a separate Hi-Color version for close-up screens, checking timing and physical display behavior before integrating.
- Keep readable text, cursor and terrain boundaries stable while ambient effects move.

Mark Ferrari's [GDC presentation](https://www.gdcvault.com/play/1023586/8-Bit-8-Bitish-Graphics) is a reference for palette-driven animation, not evidence that all of his source artwork fits Game Boy Color constraints.

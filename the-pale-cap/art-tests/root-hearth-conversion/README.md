# Root Hearth conversion candidates

Original concepts and the integrated game assets are preserved. These are offline
conversion drafts, not gameplay captures. `comparison.png` shows current / revised
at 4× nearest-neighbor scale; inspect `coherent/candidate.png` at native size too.

The current converter selects each tile's palette independently from handcrafted
ramps. Different shadow colors make flat surfaces change at tile boundaries.
The revised tool learns seven four-color families from the whole image, reserves
slot eight for UI, and jointly assigns palettes using neighboring quantization
errors. A small pixel-continuity term reduces speckled quantization while retaining
edges present in the source. No error-diffusion dithering or resampling is used.

`coherent/` is the recommended conversion draft for discussion. It has 359 unique
tiles, eight RGB555 palettes and at most four colors per tile. Its encoded 2bpp
tiles, attributes and palette data independently decode to the exact preview.
It fits the ordinary color-only background ceiling of 384 tiles. These checks
establish data legality, not artistic quality, scene integration or hardware play.

The `continuity-0`, `continuity-1`, and `continuity-4` directories retain the first
palette-assignment experiments, before pixel cleanup and corrected source RGB555
quantization. Strong continuity can flatten intentional lighting; it is not an
unconditionally better setting.

## Reproduce

Use Python with Pillow and NumPy. From the repository root:

```
python the-pale-cap/tools/convert_background.py SOURCE OUTPUT --continuity 1 --pixel-continuity .25
```

The tool is under `the-pale-cap/tools/`; source used here is
`concept-art/hideout-exploration/S01-root-hearth-160x144-composition-only.png`.
Supply paths accordingly. `--palettes PREVIOUS/audit.json` freezes previously
reviewed color families so subsequent source edits do not silently recolor them.

Each output contains native-size and enlarged previews, a manual-palette native
PNG, tile bytes, palette bytes, tile attributes and a provenance/budget audit.
Preview RGB channels use hardware five-bit values shifted left by three, matching
the native emulator's expansion. Browser color correction can display differently.

Remaining authoring work: simplify doorway silhouette and root clusters; define
the stash, threshold and preparation area as distinct editable objects; design
animation color bands deliberately; verify the whole screen with the menu open.
No candidate has replaced the game's Root Hearth.

## Material-region extension

`region-aware/` uses `lighting-regions.json`: the floor and chest light pool
share one collectively learned ramp, locked across the selected tiles. It has
325 unique tiles. `region-directed/` uses the explicitly chosen four-color ramp
in `lighting-directed.json` and has 311 tiles. Both pass encoded roundtrip and
four-colors-per-tile checks. The learned candidate reproduces exactly when its
palettes and region config are frozen. `region-comparison.png` compares the
previous candidate with the learned-region experiment.

These are alternatives for evaluation, not a new accepted art direction. One
floor palette prevents independent tile color patches but flattens some shading.
The explicit ramp explores warmer transitions and loses additional texture.
Review the actual color contours and partial boundary tiles before integration.

The added seam diagnostic marks newly introduced tile-border contrast. Its
aggregate flagged count did not improve in the region experiment, despite
removing independent floor palette choices: it also catches legitimate stepped
contours. It is a locator for review, not evidence that one image is better.
Sources, current assets and the active game preview remain intact.

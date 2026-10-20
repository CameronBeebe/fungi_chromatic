# Historical standard-color conversion experiments

This is a recipe/reference archive, not an active game build. The project moved
to Hi-Color for the integrated Hearth. Comparison images and region configs are
retained; six intermediate output directories were removed from Git tracking.
Local copies can remain, and earlier commits retain the historical results.
No integrated art or source code was removed.

The experiments compared independent tile quantization, continuity penalties,
shared material ramps and explicit lighting ramps under the ordinary GBC
four-colors-per-tile limit. `comparison.png` and `region-comparison.png` show
historical alternatives, not screenshots of the current cartridge.

To regenerate outputs from an original 160×144 source, with Pillow and NumPy:

```sh
python3 the-pale-cap/tools/convert_background.py SOURCE OUTPUT \
  --continuity 1 --pixel-continuity .25
python3 the-pale-cap/tools/convert_background.py SOURCE OUTPUT \
  --regions the-pale-cap/art-tests/root-hearth-conversion/lighting-regions.json
```

The original local input was
`concept-art/hideout-exploration/S01-root-hearth-160x144-composition-only.png`.
It is not included in a fresh clone. `lighting-directed.json` supplies an
alternative explicit ramp. `--palettes PREVIOUS/audit.json` can freeze palette
families from a locally regenerated result.

Encoded 2bpp tiles, attributes, palettes, previews and audits are generated into
the selected output folder. Seam measurements locate newly introduced contrast;
they do not establish artistic quality. Shared palettes can eliminate rectangular
color shifts while flattening intentional shading. See
[ART-PIPELINE.md](../../ART-PIPELINE.md) for the continuing authoring approach.

# Material and lighting constraints

From repository root, with Python that has NumPy and Pillow:

```
python the-pale-cap/tools/convert_background.py SOURCE OUTPUT --regions CONFIG
python the-pale-cap/tools/audit_background_seams.py SOURCE OUTPUT/candidate.png OUTPUT
```

Example config:

```json
{
  "regions": [{
    "name": "floor and continuous chest light",
    "slot": 5,
    "coverage": 0.5,
    "polygon": [[0,100],[18,84],[72,80],[159,100],[159,143],[0,143]]
  }]
}
```

Coordinates are native pixels, not enlarged-preview pixels. Each tile with at
least the specified mask coverage is locked to the zero-based palette slot.
Allowed slots are 0–6; slot 7 is reserved for this project's shared UI colors.
Conflicting overlapping locks fail. Masks are whole-tile constraints because
background hardware attributes cannot choose a new palette partway through a
tile. `region-locks-4x.png` shows affected tiles for review.

By default, a region's four-color ramp is learned from all its covered tiles
together. With `--palettes AUDIT`, the existing ramp remains fixed. Optional
`"colors": ["281828","482838","784038","B86030"]` defines a reviewed RGB
hex ramp instead; explicit region colors override a frozen palette deliberately.
They are quantized to RGB555. These overrides are art-direction decisions.
Several regions can share a slot; their complete tile set then shares one ramp.

Polygons should follow actual materials and light pools. Inspect partial boundary
tiles: the majority rule can recolor a nearby object. A single floor family
eliminates independent tile recoloring but reduces its available tones to four.
Do not conceal this tradeoff with global blur or uncontrolled dithering. Author
the needed clusters, share selected colors between palette families, or revise
the composition when a mixed tile cannot express the intended materials.

`audit.json` records source/config hashes, polygons, palettes, attributes, budget
and exact encoded roundtrip. `seams.json` ranks new tile-edge contrast and
`seams-4x.png` marks suspicious pixels in magenta. These diagnose quantization
artifacts; they cannot distinguish every intended contour from an unwanted seam.

Root Hearth examples live in `the-pale-cap/art-tests/root-hearth-conversion/`:
`lighting-regions.json` learns a shared floor ramp; `lighting-directed.json`
tests an explicit ramp. Both remain experiments, not accepted replacements.

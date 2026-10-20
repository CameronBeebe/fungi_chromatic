---
name: chromatic-art-pipeline
description: Convert and review concept artwork for The Pale Cap's native GBC backgrounds using material-region palette constraints and tile-seam diagnostics alongside the ModRetro Chromatic tools.
---

Use this project extension when turning approved visual concepts into native room
art or diagnosing palette rectangles. Read [ART-PIPELINE.md](../../the-pale-cap/ART-PIPELINE.md)
and the relevant candidate's audit before changing that asset.

Concept images establish composition, not a finished pixel master. Preserve the
original and use a separate candidate directory. Review at 160×144 as well as
enlarged. Explicit per-asset approvals govern replacement; do not infer
approval of a whole art library from approval of one example.

Run `the-pale-cap/tools/convert_background.py` with Python, Pillow and NumPy.
Use `--regions CONFIG` for continuous materials or lighting: neighboring tiles
must not choose unrelated ramps merely because their average colors differ.
Use `--palettes AUDIT` to freeze reviewed families across revisions. See
[region configuration](references/regions.md) for exact inputs and limitations.

Run `the-pale-cap/tools/audit_background_seams.py SOURCE CANDIDATE OUTPUT`.
Inspect flagged edges against the source and palette map. A lower flagged count
does not prove better artwork: intentional steps can be flagged and a uniformly
muddy picture can score well. Check specific review-identified areas.

Verify exported 2bpp roundtrip, RGB555 palettes, UI reservation and tile budget.
Then judge silhouettes, pixel clusters and readable interaction targets. Plan
palette cycling with explicit ordered indices; statistical conversion alone
does not author motion. Preserve scene-specific animation palette contracts.

After an individual candidate is approved, use the ModRetro native import/palette
tools and ROM build/playtest workflow. Separate candidate images, emulator
captures and physical-device acceptance. This skill does not authorize flashing
or modifying the installed plugin cache.

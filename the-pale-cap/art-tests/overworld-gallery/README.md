# Overworld hardware gallery

Standalone comparison ROM for the three existing overworld studies: Heartwood
Palimpsest, Chalk Lung and Velvet Estuary, each at ordinary and elevated exposure.
These are static images, including the depicted characters and resources. This
experiment does not establish a moving-actor or interactive-overworld budget.
It does not change the main game and has no save RAM.

## Build and test

From the repository root:

```sh
python3 the-pale-cap/art-tests/overworld-gallery/build.py
python3 the-pale-cap/art-tests/overworld-gallery/verify.py
```

The builder requires GBDK-2020 with `png2hicolorgb` and `lcc`. Set `GBDK_PATH`
or pass `--gbdk PATH`; one of these must identify an installed GBDK toolchain.
The verifier requires PyBoy and Pillow in its Python environment.

Source art defaults to the locally preserved, ignored directory
`concept-art/overworld-study-2026-10-11`; override with `--source PATH`.
It requires the six `01-heartwood`, `02-chalk`, and `03-velvet` PNGs named
`<direction>-<ordinary|elevated>-160x144.png`. A fresh checkout needs these local
inputs. The portfolio is deliberately not distributed with this experiment.

Generated output stays in ignored `build/`: `overworld-gallery.gbc`, converted
image data, a size/hash manifest and emulator evidence. Existing art is unchanged.

## Controls

- Start: switch between the full image and its labels/control screen.
- Left/right: choose an environment, wrapping through all three.
- A or B: toggle ordinary/elevated exposure.

The ROM boots to the control screen. No cartridge flash is part of the build.

## Measured result

The October 11 build is 128 KiB including code, font and bank padding. Its six
image payloads total 66,688 bytes: five at 11,120 bytes and one at 11,088 bytes.
This uses the existing full-screen Hi-Color study renderer; it is not a new
rendering approach. It reuses `../hearth-hicolor/src/gbc_hicolor.c` and `.h`.
See that study's README and the root third-party notices for the upstream
example's CC0 dedication and the local adaptations' MIT license.

All six images passed 180 consecutive stable-frame checks, six help round trips,
left/right wrapping and both exposure buttons in PyBoy. Genuine emulator frames
were also inspected through the plugin. Physical Chromatic evaluation is pending.
The displayed colors and controls are emulator-verified; no hardware result is
claimed. Comparing art on hardware is the next step, followed by a separate test
of modular resource states, moving characters, queued work and rendering timing.

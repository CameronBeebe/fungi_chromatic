# Third-party dependencies and notices

Checkpoint reviewed October 11, 2026. This records dependencies and copied
material; it does not relicense third-party work or choose a project-wide
license for original game code, music or concept artwork.

## GB Studio and GBVM

- [GB Studio](https://github.com/chrismaltby/gb-studio): MIT,
  Copyright (c) 2019–2026 Chris Maltby. The existing
  `the-pale-cap/LICENSE` preserves its complete notice.
- [GBVM](https://github.com/chrismaltby/gbvm): MIT, Copyright (c) 2020 Toxa.
  The local build uses source revision
  `bd6f41cc5e05cbe6601dcc7f8e2db89bed527fe3` supplied by the Chromatic toolchain.
  Its full notice is preserved in `licenses/GBVM-MIT.txt`.
- Browser study folders contain generated GB Studio preview JavaScript, CSS
  and HTML alongside the emulator. Keep these notices with redistributed previews.

## Binjgb browser emulator

[Binjgb](https://github.com/binji/binjgb) is MIT,
Copyright (c) 2016 Ben Smith. The preview runtime is the GB Studio distribution
with changes including [Daid's fork](https://github.com/daid/binjgb), as recorded
in each preview's `web/js/README.md` (or `web-preview/js/README.md`). The original
copyright and full permission notice are preserved in `licenses/BINJGB-MIT.txt`.
The WebAssembly runtime is supplied by the installed toolchain, not authored here.

## GBDK and Hi-Color

[GBDK-2020](https://github.com/gbdk-2020/gbdk-2020) is an external build dependency
with multiple component licenses. Its library uses GPLv2 with a linking exception;
do not describe the entire toolchain as MIT. Upstream's
[license overview](https://github.com/gbdk-2020/gbdk-2020/blob/develop/LICENSE)
distinguishes distributing a game ROM from distributing toolchain sources/tools.
We are not vendoring its compiler binaries or complete library source.

[png2hicolorgb](https://github.com/bbbbbr/png2hicolorgb) is the external image
converter, based on Glen Cook's public-domain code, with bbbbbr's cross-platform
port and additional components. Its complete installed distribution notice is
preserved in `licenses/GBDK-png2hicolorgb.txt`, including Wu quantizer and LodePNG
terms. Converted assets depict our concept art, not its bundled example picture.

The Hi-Color study copies and modifies GBDK 4.5.0's `examples/gb/hicolor/src/gbc_hicolor.c`
and `.h`. The example credits its palette ISR to Toxa. The installed
`LICENSE_png2hicolorgb` labels GBDK example source CC0 1.0, but the copied source
itself says `TODO: Permissive License`. Both facts are retained: do not silently
replace that header or claim that this specific ISR has an explicit MIT notice.
Before promoting the study into a release, confirm the example notice covers
this ISR or obtain an explicit clarification. This is a tracked release question,
not an assertion that the converter's output is restricted.

## External Python tools

Pillow (HPND-style license), NumPy (BSD-3-Clause), and PyBoy (LGPL-3.0) are external
dependencies used for asset preparation and test automation. Their packages are
not copied into this repository or linked into the cartridge game. Their upstream
license files govern any future redistribution of those tools:
[Pillow](https://github.com/python-pillow/Pillow),
[NumPy](https://github.com/numpy/numpy),
[PyBoy](https://github.com/Baekalfen/PyBoy).

No FlashGBX, firmware flashing tool, Wi-Fi implementation, or third-party example
art is vendored as part of this checkpoint. Concept/source images and their
variants are preserved for review; asset approval and project licensing are
separate decisions.

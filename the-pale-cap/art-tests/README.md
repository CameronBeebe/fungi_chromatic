# Local rendering experiments

Experiment source, required authoring/conversion inputs, review notes and licensed
player dependencies are versioned. Generated cartridges, build directories,
emulator saves/logs and bulky per-frame emulator evidence are ignored. Existing
copies remain on the developer's machine; cleanup removes Git tracking only.
Earlier commits retain historical copies; this is not a history rewrite.

Some older studies keep generated-looking files as required build inputs (for
example `hearth-hicolor/generated/hearth_standard.c` and `menu_font.h`). Keep
these until a reproducible generator replaces that dependency. Approved game art
under `assets/` and preserved master inputs under `art/source/` remain tracked.
The broad concept portfolio remains local under the root `concept-art/` ignore.

Rebuild a study's ROM before opening its older static web snapshot on a fresh
checkout. ROM copies under `web/rom` and `web-preview/rom` are now ignored; copy
the corresponding locally built ROM there if using those historical players.
The newer Heartwood `preview.py` prepares its ROM copy automatically. Each study's
README describes its build prerequisites and any local-only concept input.

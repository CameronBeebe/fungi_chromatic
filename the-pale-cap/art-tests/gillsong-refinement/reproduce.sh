#!/bin/sh
set -eu
cd "$(dirname "$0")"
GBDK_LCC=${GBDK_LCC:-"/Users/sciphi/Library/Application Support/modretro-chromatic/toolchain/.local/gbdk/bin/lcc"}
PYBOY_PYTHON=${PYBOY_PYTHON:-"/Users/sciphi/Library/Application Support/modretro-chromatic/toolchain/.local/pyboy-venv/bin/python"}
node prepare.cjs
"$GBDK_LCC" -Wm-yC -o gillsong-refinement.gbc main.c > build.log 2>&1
"$PYBOY_PYTHON" validate.py
"$PYBOY_PYTHON" audit-native.py

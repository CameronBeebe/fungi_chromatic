#!/bin/sh
set -eu
cd "$(dirname "$0")"
: "${GBDK_PATH:?Set GBDK_PATH to a GBDK-2020 installation}"
GBDK_LCC="$GBDK_PATH/bin/lcc"
PYBOY_PYTHON=${PYBOY_PYTHON:-python3}
[ -x "$GBDK_LCC" ] || { echo "GBDK_PATH must contain executable bin/lcc" >&2; exit 1; }
node prepare.cjs
"$GBDK_LCC" -Wm-yC -o gillsong-refinement.gbc main.c > build.log 2>&1
"$PYBOY_PYTHON" validate.py
"$PYBOY_PYTHON" audit-native.py

#!/bin/sh
set -eu
: "${GBDK_PATH:?Set GBDK_PATH to a GBDK-2020 installation containing bin/lcc and bin/png2hicolorgb}"
gbdk_path="$GBDK_PATH"
[ -x "$gbdk_path/bin/lcc" ] && [ -x "$gbdk_path/bin/png2hicolorgb" ] || {
  echo "GBDK_PATH must contain executable bin/lcc and bin/png2hicolorgb" >&2
  exit 1
}
gbdk_path=$(cd "$gbdk_path" && pwd)
cd "$(dirname "$0")"
mkdir -p bin generated
"$gbdk_path/bin/png2hicolorgb" ../../art/source/root-hearth-160x144.png --type=3 -L=adaptive-fast -R=adaptive-fast --csource --bank=255 -o generated/hearth_hicolor.c
"$gbdk_path/bin/png2hicolorgb" generated/hearth_menu_source.png --type=3 -L=adaptive-fast -R=adaptive-fast --csource --bank=255 -o generated/hearth_menu.c
"$gbdk_path/bin/lcc" -Wm-yC -Wl-yt0x19 -autobank -Wb-ext=.rel -Isrc -Igenerated -o bin/hearth-hicolor.gbc src/main.c src/gbc_hicolor.c generated/hearth_hicolor.c generated/hearth_menu.c generated/hearth_standard.c
mkdir -p web/rom
cp bin/hearth-hicolor.gbc web/rom/hearth-hicolor.gbc

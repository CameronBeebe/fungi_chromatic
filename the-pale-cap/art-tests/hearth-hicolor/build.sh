#!/bin/sh
set -eu
gbdk_path="${GBDK_PATH:-/Users/sciphi/Library/Application Support/modretro-chromatic/toolchain/.local/gbdk}"
cd "$(dirname "$0")"
"$gbdk_path/bin/png2hicolorgb" ../../art/source/root-hearth-160x144.png --type=3 -L=adaptive-fast -R=adaptive-fast --csource --bank=255 -o generated/hearth_hicolor.c
"$gbdk_path/bin/png2hicolorgb" generated/hearth_menu_source.png --type=3 -L=adaptive-fast -R=adaptive-fast --csource --bank=255 -o generated/hearth_menu.c
"$gbdk_path/bin/lcc" -Wm-yC -Wl-yt0x19 -autobank -Wb-ext=.rel -Isrc -Igenerated -o bin/hearth-hicolor.gbc src/main.c src/gbc_hicolor.c generated/hearth_hicolor.c generated/hearth_menu.c generated/hearth_standard.c

#pragma bank 255
#include <gbdk/platform.h>
#include "vm.h"

/* Vermilion study: only the cyan ornament palette moves. Each band gets
 * sixteen frames of light, followed by 144 frames at the original colors.
 * Called once per VM frame only while the inspection scene is open. */
static UBYTE tick;
void ff_gillsong(SCRIPT_CTX *THIS) OLDCALL BANKED {
    UWORD colors[4];
    UBYTE phase;
    if (*(UWORD *)VM_REF_TO_PTR(-1) == 0) tick = 0;
    colors[0] = 3105; colors[1] = 12611;
    colors[2] = 21061; colors[3] = 28558;
    phase = tick >> 3;
    if (phase < 6) {
        colors[3] = 21061;
        colors[1 + (phase >> 1)] = 28558;
    }
    set_bkg_palette(6, 1, colors);
    if (++tick == 192) tick = 0;
}

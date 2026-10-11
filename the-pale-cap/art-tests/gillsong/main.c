#include <gb/gb.h>
#include <gb/cgb.h>
#include <stdint.h>
#include "art.h"

// Standalone screen study. No game assets, saves or ROM are modified.
void main(void) {
    uint8_t tick=0, phase=0, cycling=0, keys;
    uint16_t cycle[4];
    DISPLAY_OFF;
    set_bkg_palette(0,8,art_palettes);
    VBK_REG=0;
    set_bkg_data(0,TILE_COUNT>256?0:(uint8_t)TILE_COUNT,art_tiles);
#if TILE_COUNT > 256
    VBK_REG=1;
    set_bkg_data(0,TILE_COUNT-256,art_tiles+4096);
#endif
    VBK_REG=1; set_bkg_tiles(0,0,20,18,art_attrs);
    VBK_REG=0; set_bkg_tiles(0,0,20,18,art_map);
    SHOW_BKG; HIDE_SPRITES; DISPLAY_ON;
    while(1) {
        vsync(); keys=joypad();
        if(keys&J_A)cycling=1;
        if(keys&J_B){cycling=0;set_bkg_palette(0,8,art_palettes);}
        if(cycling && ++tick>=10){
            tick=0;phase=(phase+1)%3;
            cycle[0]=art_palettes[24];
            cycle[1]=art_palettes[25+phase];
            cycle[2]=art_palettes[25+(phase+1)%3];
            cycle[3]=art_palettes[25+(phase+2)%3];
            set_bkg_palette(6,1,cycle);
        }
    }
}

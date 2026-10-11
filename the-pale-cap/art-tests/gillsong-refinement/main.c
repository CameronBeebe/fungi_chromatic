#include <gb/gb.h>
#include <gb/cgb.h>
#include <stdint.h>
#include "art.h"
// Standalone normal-color art study. No game state, save RAM or item mechanics.
static uint8_t theme=0,flow=0,tick=0,phase=0;
static void still(void){set_bkg_palette(0,8,art_palettes+(uint16_t)theme*32);}
static void animate(void){
 uint16_t p[4]; uint8_t i;
 const uint16_t *base=art_palettes+(uint16_t)theme*32+24;
 for(i=0;i<4;i++)p[i]=base[i];
 // Root, middle, tip each brighten in turn. Long rest preserves the still.
 if(phase<6){p[1]=base[1];p[2]=base[2];p[3]=base[2];p[1+phase/2]=base[3];}
 set_bkg_palette(6,1,p);
}
void main(void){
 uint8_t keys,old=0,press;
 DISPLAY_OFF;VBK_REG=0;set_bkg_data(0,TILE_COUNT,art_tiles);
 VBK_REG=1;set_bkg_tiles(0,0,20,18,art_attrs);
 VBK_REG=0;set_bkg_tiles(0,0,20,18,art_map);
 still();SHOW_BKG;HIDE_SPRITES;DISPLAY_ON;
 while(1){vsync();keys=joypad();press=keys&~old;old=keys;
  if(press&(J_RIGHT|J_SELECT)){theme=(theme+1)%3;flow=0;still();}
  if(press&J_LEFT){theme=theme?theme-1:2;flow=0;still();}
  if(press&J_A){flow=1;phase=0;tick=0;animate();}
  if(press&J_B){flow=0;still();}
  if(flow&&++tick==8){tick=0;phase=(phase+1)%24;animate();}
 }
}

#include <gbdk/platform.h>
#include "gbc_hicolor.h"
#include "hearth_hicolor.h"
#include "hearth_standard.h"
#include "hearth_menu.h"
#include "menu_font.h"

/* Separate renderer study. A: Hi-Color, B: standard, Select: toggle.
 * No save RAM, production gameplay, or cartridge-writing code. */
static uint8_t render_mode = 1;
static uint8_t menu_open, choice;
const uint16_t ui_colors[] = {RGB(1,1,3),RGB(3,8,10),RGB(6,24,25),RGB(31,29,24)};
// Fixed ROM bank, byte order required by the ISR extension.
const uint8_t hearth_ui_palette[] = {0x21,0x0c,0x03,0x29,0x06,0x67,0xbf,0x63};

static void menu_text(uint8_t x,uint8_t y,const char *text) {
    uint8_t tile;
    while (*text) {
        tile=128+font_index[(uint8_t)*text++];
        VBK_REG=0;set_win_tiles(x,y,1,1,&tile);
        tile=15;VBK_REG=1;set_win_tiles(x,y,1,1,&tile);++x;
    }
    VBK_REG=0;
}

static void draw_menu(void) {
    VBK_REG=1;set_bkg_data(128,FONT_COUNT,menu_font);
    fill_win_rect(0,0,20,5,15);
    VBK_REG=0;fill_win_rect(0,0,20,5,128);
    menu_text(4,1,"ROOT HEARTH");
    menu_text(2,3,"BAG");menu_text(8,3,"HOME");menu_text(15,3,"EXIT");
    menu_text(1,3,choice==0?">":" ");menu_text(7,3,choice==1?">":" ");menu_text(14,3,choice==2?">":" ");
    move_win(7,104);SHOW_WIN;
}

static void show_image(void) {
    uint8_t bank = CURRENT_BANK;
    vsync(); DISPLAY_OFF; hicolor_stop(); HIDE_WIN; HIDE_SPRITES;
    SCX_REG = SCY_REG = 0;
    hicolor_menu_enabled=menu_open;
    if (render_mode) {
        if (menu_open)hicolor_start(&hearth_menu_data, BANK(hearth_menu));
        else hicolor_start(&hearth_hicolor_data, BANK(hearth_hicolor));
    }
    else {
        SWITCH_ROM(BANK(hearth_standard));
        VBK_REG = 0; set_bkg_data(0,256,standard_tiles);
        set_bkg_tiles(0,0,20,18,standard_map);
        VBK_REG = 1; set_bkg_data(0,104,standard_tiles+4096);
        set_bkg_tiles(0,0,20,18,standard_attrs);
        VBK_REG = 0; set_bkg_palette(0,8,standard_palettes);
        SWITCH_ROM(bank);
    }
    if (menu_open) {set_bkg_palette(7,1,ui_colors);draw_menu();}
    SHOW_BKG; DISPLAY_ON;
}

void main(void) {
    uint8_t old = 0, keys, press;
    if (_cpu != CGB_TYPE) return;
    cpu_fast(); show_image();
    while (1) {
        vsync(); keys=joypad(); press=keys & ~old; old=keys;
        if (press & J_START) {menu_open=!menu_open;show_image();}
        else if (menu_open && (press & J_LEFT)) {choice=choice?choice-1:2;draw_menu();}
        else if (menu_open && (press & J_RIGHT)) {choice=(choice+1)%3;draw_menu();}
        else if (menu_open && (press & (J_A|J_B))) {menu_open=0;show_image();}
        else if (press & J_A) { render_mode=1; show_image(); }
        else if (press & J_B) { render_mode=0; show_image(); }
        else if (press & J_SELECT) { render_mode=!render_mode; show_image(); }
    }
}

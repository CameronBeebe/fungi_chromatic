#include <gbdk/platform.h>
#include <gbdk/font.h>
#include <gbdk/console.h>
#include <stdio.h>
#include "gbc_hicolor.h"
#include "gallery_images.h"

/* Static image comparison only. No production state or battery SRAM. */
static uint8_t direction, exposure, help_open = 1;
static const char * const names[] = {"HEARTWOOD", "CHALK LUNG", "VELVET ESTUARY"};
static const uint16_t black[32] = {0};
static const uint16_t ui[] = {RGB(1,1,3), RGB(3,8,10), RGB(6,24,25), RGB(31,29,24)};
/* Required by the reused study renderer; its cropped-menu mode stays disabled. */
const uint8_t hearth_ui_palette[] = {0x21,0x0c,0x03,0x29,0x06,0x67,0xbf,0x63};

static void prepare(void) {
    vsync();
    hicolor_stop();
    set_bkg_palette(0,8,black);
    HIDE_WIN; HIDE_SPRITES;
    VBK_REG = 0;
    SCX_REG = SCY_REG = 0;
}

static void show_help(void) {
    prepare();
    /* The console uses signed tile addressing; clear old image attributes. */
    VBK_REG = 1; fill_bkg_rect(0,0,20,18,0); VBK_REG = 0;
    font_init(); font_color(3,0); font_set(font_load(font_min));
    cls();
    gotoxy(1,1); printf("THE PALE CAP");
    gotoxy(1,3); printf("ART GALLERY");
    gotoxy(1,5); printf("%u/3 %s",direction+1,names[direction]);
    gotoxy(1,7); printf(exposure ? "ELEVATED EXPOSURE" : "ORDINARY EXPOSURE");
    gotoxy(1,10); printf("LEFT/RIGHT: PLACE");
    gotoxy(1,11); printf("A/B: EXPOSURE");
    gotoxy(1,12); printf("START: VIEW/HELP");
    gotoxy(1,15); printf("STATIC ART STUDY");
    gotoxy(1,16); printf("NO GAMEPLAY/SAVE");
    vsync(); set_bkg_palette(0,1,ui); SHOW_BKG;
}

static void show_image(void) {
    uint8_t index = direction*2+exposure;
    prepare();
    /* Hi-Color data uses unsigned tile IDs across both VRAM banks. */
    LCDC_REG |= LCDCF_BG8000;
    hicolor_menu_enabled = 0;
    hicolor_start(gallery_images[index],gallery_bank(index));
    SHOW_BKG;
}

void main(void) {
    uint8_t previous=0,keys,pressed;
    if (_cpu != CGB_TYPE) return;
    cpu_fast(); show_help();
    while (1) {
        vsync(); keys=joypad(); pressed=keys & ~previous; previous=keys;
        if (pressed & J_START) help_open=!help_open;
        else if (pressed & J_LEFT) direction=direction ? direction-1 : 2;
        else if (pressed & J_RIGHT) direction=(direction+1)%3;
        else if (pressed & (J_A|J_B)) exposure=!exposure;
        else continue;
        if (help_open) show_help(); else show_image();
    }
}

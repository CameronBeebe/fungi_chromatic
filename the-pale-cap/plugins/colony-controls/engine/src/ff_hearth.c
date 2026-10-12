// Derived from GBDK-2020 4.5.0 examples/gb/hicolor (Toxa palette ISR).
// Upstream header: TODO: Permissive License. See THIRD_PARTY_NOTICES.md.
// Local changes: engine VRAM layout, 104px window split, lifecycle and music clock.
#pragma bank 255
#include <gbdk/platform.h>
#include "vm.h"
#include "interrupts.h"
#include "palette.h"
#include "music_manager.h"
#include "ff_hearth_data.h"

static uint16_t ff_hearth_sp_save;
static uint8_t ff_hearth_stat_save;
static const uint8_t *ff_hearth_palettes;
static uint8_t ff_hearth_bank;
static uint8_t ff_hearth_last_scanline;
static uint8_t ff_hearth_active;
static uint8_t ff_hearth_loaded;
static uint8_t ff_hearth_timer_ie;
static uint16_t ff_hearth_music_phase;
static uint8_t ff_hearth_ui_palette[8];

// ISR function which updates 4 CGB palettes per scanline
// alternating between Palettes 0-3 and 4-7
void ff_hearth_lcd(void) NONBANKED {
__asm
        ldh a, (__current_bank)     ; switch ROM bank
        push af
        ld a, (_ff_hearth_bank)
        or a
        jr z, 3$
        ldh (__current_bank), a
        ld (_rROMB0), a
3$:
        ld (_ff_hearth_sp_save), sp           ; save SP

        ld hl, #_ff_hearth_palettes ; load address of picture palettes buffer
        ld a, (hl+)
        ld d, (hl)
        ld e, a

        ldh a, (_SCY_REG)
        swap a
        ld l, a
        and #0x0f
        ld h, a
        ld a, #0xf0
        and l
        ld l, a
        add hl, hl
        add hl, de                  ; offset address by SCY * (4 * 4 * 2)
        ld sp, hl

        rlca                        ; compensate odd/even line
        and #0x20                   ; if odd then start from 4-th palette; offset == 32
        or  #BCPSF_AUTOINC          ; set auto-increment

        ld hl, #_BCPS_REG
        ld (hl+), a                 ; HL now points to BCPD

        ld c, #(8 * 4)              ; read and set the the colors that come from previous lines
2$:
        pop de
        ld (hl), e
        ld (hl), d
        dec c
        jr nz, 2$

0$:
        ldh a, (_STAT_REG)
        and #STATF_BUSY
        jr z, 0$                    ; wait for mode 3

        ldh a, (_STAT_REG)
        ld (_ff_hearth_stat_save), a

        ld a, #STATF_MODE00
        ldh (_STAT_REG), a
        xor a
        ldh (_IF_REG), a

1$:
        pop bc                      ; preload the first two colors
        pop de

        xor a
        ldh (_IF_REG), a
        halt                        ; wait for mode 0

        ld (hl), c                  ; set the first two colors
        ld (hl), b
        ld (hl), e
        ld (hl), d

        .rept (4*4)-2               ; read and set four palettes except the two previously set colors
            pop de
            ld (hl), e
            ld (hl), d
        .endm

        ld a, (_ff_hearth_last_scanline)
        ld c, a
        ldh a, (_LY_REG)
        cp c
        jr c, 1$                    ; load the next 4 palettes

        ; The final image row already has its palettes. Wait for its
        ; HBlank and restore only the UI colors, without a redundant 32-byte
        ; palette write that would spill into the first window scanline.
6$:
        ldh a, (_LY_REG)
        cp #103
        jr nz, 6$
7$:
        ldh a, (_STAT_REG)
        and #STATF_BUSY
        jr nz, 7$
        ld a, (_ff_hearth_active)
        or a
        jr z, 4$
        ld a, #0xb8
        ldh (_BCPS_REG), a
        ld hl, #_ff_hearth_ui_palette
        ld c, #0x69
        ld b, #8
5$:
        ld a, (hl+)
        ldh (c), a
        dec b
        jr nz, 5$
4$:

        ld a, (_ff_hearth_stat_save)
        ldh (_STAT_REG), a
        xor a
        ldh (_IF_REG), a

        ld sp, #_ff_hearth_sp_save
        pop hl
        ld sp, hl                   ; restore SP

        pop af
        ldh (__current_bank), a
        ld (_rROMB0), a

        ret
__endasm;
}



/* The scanline loop masks interrupts across the picture. Clock the existing
 * music driver from VBlank while it owns LCD timing, preserving its 256 Hz
 * logical clock: 70224 dots/frame / 16384 dots/timer tick = 4389/1024.
 * There are no streaming sound effects or link transfers in this home view.
 * Full menus and other scenes retain the engine timer interrupt unchanged. */
void ff_hearth_music(void) NONBANKED {
    ff_hearth_music_phase += 4389;
    while (ff_hearth_music_phase >= 1024) {
        ff_hearth_music_phase -= 1024;
        music_play_isr();
    }
}

static void hearth_stop(void) NONBANKED {
    if (!ff_hearth_active) return;
    CRITICAL {
        remove_LCD(ff_hearth_lcd);
        remove_VBL(ff_hearth_music);
        ff_hearth_active = 0;
        STAT_REG = STATF_LYC;
        LYC_REG = 150;
        add_LCD(simple_LCD_isr);
        IF_REG &= ~TIM_IFLAG;
        IE_REG = (IE_REG & ~TIM_IFLAG) | ff_hearth_timer_ie;
    }
    set_bkg_palette(0, 8, (const uint16_t *)BkgPalette);
}

static void hearth_start(void) NONBANKED {
    uint8_t saved_bank, i;
    if (ff_hearth_active) return;
    wait_vbl_done();
    DISPLAY_OFF;
    /* All image tiles stay outside the engine UI/font allocation. Bank 0 uses
     * IDs 0..127 and bank 1 uses 0..131 in signed background addressing. */
    LCDC_REG &= ~LCDCF_BG8000;
    if (!ff_hearth_loaded) {
        saved_bank = CURRENT_BANK;
        SWITCH_ROM(BANK(ff_hearth_data));
        VBK_REG = 0;
        set_bkg_data(0, 128, ff_hearth_tiles);
        set_bkg_tiles(0, 0, 20, 13, ff_hearth_map);
        VBK_REG = 1;
        set_bkg_data(0, 132, ff_hearth_tiles + 2048);
        set_bkg_tiles(0, 0, 20, 13, ff_hearth_attrs);
        VBK_REG = 0;
        SWITCH_ROM(saved_bank);
        ff_hearth_loaded = 1;
    }
    for (i = 0; i != 8; ++i)
        ff_hearth_ui_palette[i] = ((uint8_t *)&BkgPalette[7])[i];
    ff_hearth_bank = BANK(ff_hearth_data);
    ff_hearth_palettes = ff_hearth_colors;
    ff_hearth_last_scanline = 102;
    SCX_REG = SCY_REG = 0;
    CRITICAL {
        remove_LCD(simple_LCD_isr);
        ff_hearth_timer_ie = IE_REG & TIM_IFLAG;
        IE_REG &= ~TIM_IFLAG;
        ff_hearth_active = 1;
        add_VBL(ff_hearth_music);
        add_LCD(ff_hearth_lcd);
        LYC_REG = 152;
        STAT_REG = STATF_LYC;
    }
    DISPLAY_ON;
}

/* 0: leave scene/reset loader; 1: show room; 2: full-screen menu.
 * Called only by the home event. Normal expedition menus never take ownership. */
void ff_hearth(SCRIPT_CTX *THIS) OLDCALL BANKED {
    uint8_t mode = *(UWORD *)VM_REF_TO_PTR(-1);
    if (mode == 1) hearth_start();
    else {
        hearth_stop();
        if (!mode) ff_hearth_loaded = 0;
    }
}

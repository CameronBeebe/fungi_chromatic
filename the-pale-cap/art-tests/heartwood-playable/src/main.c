#include <gbdk/platform.h>
#include <gbdk/font.h>
#include <gbdk/console.h>
#include <stdio.h>
#include "gbc_hicolor.h"
#include "master.h"
#include "assets.h"
#ifdef SCENE_CONFIGURED
#include <scene_config.h>
#else
#include "scene_defaults.h"
#endif
extern void hicolor_palette_isr(void) NONBANKED;
uint8_t route_step(uint8_t sx,uint8_t sy,uint8_t tx,uint8_t ty) BANKED;

/* Isolated rendering/gameplay test. No saves, production scripts or audio.
 * Cursor repeat and FIFO orders follow ff_controls.c's established model.
 * Its ROM-banked VM adapter / precomputed world routes aren't reusable here. */
const uint8_t hearth_ui_palette[] = {0x42,0x10,0,0,0,0,0xbf,0x63};
static const uint16_t black[32]={0};
static const uint16_t ui[4]={RGB(2,2,4),RGB(6,10,12),RGB(15,22,22),RGB(28,26,20)};
typedef struct {uint8_t x,y,harvest;} Order;
static Order orders[8];
uint8_t queue_count,bram_x=SCENE_SPAWN_X*8+4,bram_y=SCENE_SPAWN_Y*8+4,cursor_x=14,cursor_y=11;
uint8_t supplies=SCENE_START_SUPPLIES;
uint8_t harvested,exposure,loot,work_ticks,help_open=1,rejected;
static uint8_t facing=4,previous,last_dir,frame_clock,last_cursor_time,cursor_delay;
static uint8_t patch_pending,resource_index,reveal_index;
uint8_t moving,notice,notice_ticks;
static uint8_t next_x,next_y,step_remaining,hud_last=255,priority_x=255,priority_y=255;
static uint8_t hud[20],priority_attrs[8];
enum {MSG_NONE,MSG_QUEUED,MSG_HARVEST,MSG_CUT,MSG_BLOCKED,MSG_FULL,MSG_DUPLICATE,MSG_ON,MSG_OFF,MSG_RESET,MSG_EMPTY,MSG_COST};
static void say(uint8_t msg){notice=msg;notice_ticks=75;}

static uint16_t cell(uint8_t x,uint8_t y){return (uint16_t)y*20+x;}
static void pop_order(void){
    uint8_t i;
    for(i=1;i<queue_count;i++)orders[i-1]=orders[i];
    if(queue_count)--queue_count;
    work_ticks=moving=step_remaining=0;
    priority_x=255;
}
static void run_orders(void){
    uint8_t direction;
    if(!queue_count)return;
    if(!step_remaining){
        direction=route_step(bram_x/8,bram_y/8,orders[0].x,orders[0].y);
        if(direction==255){rejected=30;say(MSG_BLOCKED);pop_order();return;}
        if(direction==4){
            moving=0;
            if(orders[0].harvest&&!harvested){
                if(supplies<SCENE_HARVEST_COST){say(MSG_COST);pop_order();return;}
                if(++work_ticks==1)say(MSG_HARVEST);
                if(work_ticks==SCENE_WORK_TICKS){harvested=1;loot=SCENE_HARVEST_YIELD;supplies-=SCENE_HARVEST_COST;patch_pending|=1;resource_index=0;pop_order();say(MSG_CUT);}
            }else pop_order();
            return;
        }
        next_x=bram_x;next_y=bram_y;step_remaining=8;
        if(direction==0){next_x-=8;facing=8;}if(direction==1){next_x+=8;facing=4;}
        if(direction==2){next_y-=8;facing=2;}if(direction==3){next_y+=8;facing=0;}
    }
    moving=1;
    if(bram_x<next_x)++bram_x;else if(bram_x>next_x)--bram_x;
    if(bram_y<next_y)++bram_y;else if(bram_y>next_y)--bram_y;
    --step_remaining;
}
static void designate(void){
    uint8_t i,is_resource=cursor_x>=13&&cursor_x<=16&&cursor_y>=10&&cursor_y<=12;
    if(queue_count==8){rejected=30;say(MSG_FULL);return;}
    if(is_resource){
        if(harvested){rejected=30;say(MSG_EMPTY);return;}
        if(supplies<SCENE_HARVEST_COST){rejected=30;say(MSG_COST);return;}
        for(i=0;i<queue_count;i++)if(orders[i].harvest){rejected=30;say(MSG_DUPLICATE);return;}
        orders[queue_count].x=SCENE_WORK_X;orders[queue_count].y=SCENE_WORK_Y;
    }else{
        if(!walkable[cell(cursor_x,cursor_y)]){rejected=30;say(MSG_BLOCKED);return;}
        orders[queue_count].x=cursor_x;orders[queue_count].y=cursor_y;
    }
    orders[queue_count++].harvest=is_resource;
    priority_x=255;
    say(MSG_QUEUED);
}
static void cursor_input(uint8_t keys,uint8_t pressed){
    uint8_t held=keys&(J_LEFT|J_RIGHT|J_UP|J_DOWN),dir=pressed&held,now=(uint8_t)sys_time;
    if(!dir)dir=(held&last_dir)?last_dir:held;
    dir=dir&J_LEFT?J_LEFT:dir&J_RIGHT?J_RIGHT:dir&J_UP?J_UP:dir&J_DOWN?J_DOWN:0;
    if(!dir){last_dir=0;return;}
    if(!(pressed&dir)&&dir==last_dir&&(uint8_t)(now-last_cursor_time)<cursor_delay)return;
    cursor_delay=dir==last_dir?3:6;last_dir=dir;last_cursor_time=now;
    if(dir==J_LEFT&&cursor_x)--cursor_x;
    if(dir==J_RIGHT&&cursor_x<19)++cursor_x;
    if(dir==J_UP&&cursor_y)--cursor_y;
    if(dir==J_DOWN&&cursor_y<16)++cursor_y;
}
static void pair(uint8_t obj,uint8_t tile,uint8_t x,uint8_t y,uint8_t prop){
    set_sprite_tile(obj,tile);set_sprite_prop(obj,prop);move_sprite(obj,x+8,y+16);
    set_sprite_tile(obj+1,tile+2);set_sprite_prop(obj+1,prop);move_sprite(obj+1,x+16,y+16);
}
/* The visible 8x8 bracket encloses the selected cell. Bram stands at its
 * center; the ground-order pin tip lands on that same center. */
static void draw_cursor(void){
    pair(0,192,cursor_x*8,cursor_y*8,S_BANK|(rejected?3:2));
}
static void draw_actors(void){
    uint8_t f=work_ticks?6+((frame_clock>>3)&1):(facing==8?4:facing)+(moving?((frame_clock>>3)&1):0);
    uint8_t flip=facing==8?S_FLIPX:0,i;
    /* Swap the halves as well as their pixels when facing left. */
    for(i=0;i<4;i++){
        uint8_t half=i&1,layer=i>>1;
        set_sprite_tile(i+3,128+f*8+layer*4+(flip?(1-half):half)*2);
        set_sprite_prop(i+3,S_BANK|layer|flip);
        move_sprite(i+3,bram_x+half*8,bram_y);
    }
    /* Lowest OAM indices win: UI stays above Bram when their pixels overlap. */
    if(queue_count){
        set_sprite_tile(2,196+(work_ticks&&((frame_clock>>3)&1)?2:0));set_sprite_prop(2,S_BANK|2);
        move_sprite(2,orders[0].harvest?122:orders[0].x*8+9,orders[0].harvest?85:orders[0].y*8+12);
    }else move_sprite(2,0,0);
    if(exposure){
        set_sprite_tile(7,200+((frame_clock>>4)&1)*2);set_sprite_prop(7,S_BANK|4);move_sprite(7,97,84);
    }else move_sprite(7,0,0);
}

static void cursor_priority(void){
    uint8_t i,x,y;
    if(cursor_x==priority_x&&cursor_y==priority_y)return;
    priority_x=cursor_x;priority_y=cursor_y;
    for(i=0;i<8;i++){
        x=4+(i&3);y=7+(i>>2);priority_attrs[i]=foreground_attrs[i];
        if(x==cursor_x&&y==cursor_y)priority_attrs[i]&=0x7f;
        if(queue_count&&!orders[0].harvest&&x==orders[0].x&&(y==orders[0].y||y+1==orders[0].y))priority_attrs[i]&=0x7f;
    }
    VBK_REG=1;set_bkg_tiles(4,7,4,2,priority_attrs);VBK_REG=0;
}
static uint8_t glyph(char c){
    if(c>='A'&&c<='Z')return 205+c-'A';
    if(c>='0'&&c<='9')return 231+c-'0';
    if(c==':')return 241;if(c=='+')return 242;if(c=='-')return 243;
    return 204;
}
static void draw_status(void){
    const char *text;uint8_t key,i;
    key=notice_ticks?notice:work_ticks?MSG_HARVEST:moving?20:exposure?21:22;
    if(key==hud_last)return;hud_last=key;
    switch(key){
    case MSG_QUEUED:text="ORDER QUEUED";break;
    case MSG_HARVEST:text="HARVESTING";break;
    case MSG_CUT:text=SCENE_REWARD_MESSAGE;break;
    case MSG_COST:text="NEED MORE SUPPLIES";break;
    case MSG_BLOCKED:text="CANNOT WALK THERE";break;
    case MSG_FULL:text="QUEUE FULL";break;
    case MSG_DUPLICATE:text="ALREADY QUEUED";break;
    case MSG_ON:case 21:text="REVEAL TEST ON";break;
    case MSG_OFF:text="REVEAL TEST OFF";break;
    case MSG_RESET:text="ROOM RESET";break;
    case MSG_EMPTY:text="PATCH HARVESTED";break;
    case 20:text="WALKING TO ORDER";break;
    default:text="A ORDER  B REVEAL";
    }
    for(i=0;i<20;i++)hud[i]=204;
    for(i=0;text[i]&&i<20;i++)hud[i]=glyph(text[i]);
    VBK_REG=0;set_win_tiles(0,0,20,1,hud);
}
static void patch_tile(uint16_t id,const uint8_t *data){
    VBK_REG=id>=256?1:0;set_bkg_data((uint8_t)id,1,data);VBK_REG=0;
}
static void update_patch(void){
    /* One tile per VBlank, prioritizing harvest; avoids overrunning the palette
     * ISR's LYC=152 start. At most 12 refreshes, no full-scene reload/blank. */
    if(patch_pending&1){
        patch_tile(resource_ids[resource_index],(harvested?resource_cut:resource_full)+resource_index*16);
        if(++resource_index==12){patch_pending&=~1;resource_index=0;}
    }else if(patch_pending&2){
        patch_tile(reveal_ids[reveal_index],(exposure?reveal_on:reveal_off)+reveal_index*16);
        if(++reveal_index==10){patch_pending&=~2;reveal_index=0;}
    }
}
static void prepare(void){
    vsync();hicolor_stop();set_bkg_palette(0,8,black);HIDE_SPRITES;HIDE_WIN;VBK_REG=0;
}
static void show_help(void){
    prepare();VBK_REG=1;fill_bkg_rect(0,0,20,18,0);VBK_REG=0;
    font_init();font_color(3,0);font_set(font_load(font_min));cls();
    gotoxy(1,1);printf("HEARTWOOD STUDY");
    gotoxy(1,3);printf("DPAD  MOVE CURSOR");
    gotoxy(1,5);printf("A  WALK OR HARVEST");
    gotoxy(1,7);printf("B  REVEAL ART TEST");
    gotoxy(1,9);printf("SELECT  RESET ROOM");
    gotoxy(1,11);printf("START  VIEW OR HELP");
    gotoxy(1,13);printf("BAG %u  ORDERS %u",loot,queue_count);
    gotoxy(1,15);printf("SUPPLIES %u",supplies);
    gotoxy(1,16);printf("NO SAVE OR AUDIO");
    vsync();set_bkg_palette(0,1,ui);SHOW_BKG;
}
static void show_room(void){
    uint8_t i;
    prepare();LCDC_REG|=LCDCF_BG8000|LCDCF_WIN9C00;hicolor_menu_enabled=1;
    /* Load under black, retain the renderer's palette pointer but defer its ISR
     * until sprites and persistent state patches are also ready. */
    CRITICAL { hicolor_start(&master_data,2); hicolor_stop(); }
    for(i=0;i<12;i++)patch_tile(resource_ids[i],(harvested?resource_cut:resource_full)+i*16);
    for(i=0;i<10;i++)patch_tile(reveal_ids[i],(exposure?reveal_on:reveal_off)+i*16);
    VBK_REG=1;set_sprite_data(128,64,bram_tiles);set_sprite_data(192,4,cursor_tiles);
    set_sprite_data(196,8,icon_tiles);set_bkg_data(204,HUD_FONT_COUNT,hud_font);
    fill_win_rect(0,0,20,1,15);VBK_REG=0;move_win(7,136);
    set_sprite_palette(0,2,actor_palettes);set_sprite_palette(2,2,cursor_palettes);
    set_sprite_palette(4,1,reveal_palette);
    patch_pending=resource_index=reveal_index=0;priority_x=255;cursor_priority();
    hud_last=255;draw_status();draw_cursor();draw_actors();SHOW_BKG;SHOW_SPRITES;SHOW_WIN;
    CRITICAL { LYC_REG=152;STAT_REG=STATF_LYC;add_LCD(hicolor_palette_isr); }
}
void main(void){
    uint8_t keys,pressed;
    if(_cpu!=CGB_TYPE)return;
    cpu_fast();SPRITES_8x16;show_help();
    while(1){
        vsync();++frame_clock;keys=joypad();pressed=keys&~previous;previous=keys;
        if(pressed&J_START){help_open=!help_open;if(help_open)show_help();else show_room();continue;}
        if(help_open)continue;
        cursor_input(keys,pressed);draw_cursor();
        /* Default GBDK DMA precedes main-loop input sampling. Refresh updated
         * UI while still safely in early VBlank, before the LYC=152 renderer. */
        if(LY_REG>=144&&LY_REG<149)refresh_OAM();
        cursor_priority();
        if(pressed&J_A)designate();
        if(pressed&J_B){exposure=!exposure;patch_pending|=2;reveal_index=0;say(exposure?MSG_ON:MSG_OFF);}
        if(pressed&J_SELECT){
            queue_count=work_ticks=harvested=loot=exposure=moving=step_remaining=0;
            patch_pending=3;resource_index=reveal_index=0;bram_x=SCENE_SPAWN_X*8+4;bram_y=SCENE_SPAWN_Y*8+4;
            supplies=SCENE_START_SUPPLIES;priority_x=255;say(MSG_RESET);
        }
        /* Logic may resume after the long LCD ISR; no hardware writes here
         * except shadow OAM, which the next VBlank transfers. */
        run_orders();if(rejected)--rejected;if(notice_ticks)--notice_ticks;draw_actors();
        update_patch();draw_status();
    }
}

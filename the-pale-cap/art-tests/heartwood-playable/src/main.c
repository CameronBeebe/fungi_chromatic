#include <gbdk/platform.h>
#include <gbdk/font.h>
#include <gbdk/console.h>
#include <stdio.h>
#include "gbc_hicolor.h"
#include "master.h"
#include "assets.h"
extern void hicolor_palette_isr(void) NONBANKED;

/* Isolated rendering/gameplay test. No saves, production scripts or audio.
 * Cursor repeat and FIFO orders follow ff_controls.c's established model.
 * Its ROM-banked VM adapter / precomputed world routes aren't reusable here. */
const uint8_t hearth_ui_palette[] = {0};
static const uint16_t black[32]={0};
static const uint16_t ui[4]={RGB(2,2,4),RGB(6,10,12),RGB(15,22,22),RGB(28,26,20)};
typedef struct {uint8_t x,y,harvest;} Order;
static Order orders[8];
uint8_t queue_count,bram_x=44,bram_y=100,cursor_x=14,cursor_y=11;
uint8_t harvested,exposure,loot,work_ticks,help_open=1,rejected;
static uint8_t facing=4,previous,repeat,last_dir,frame_clock;
static uint8_t patch_pending,resource_index,reveal_index;
static uint16_t parents[360],search[360],search_head,search_tail;
static uint16_t path[360],path_length,path_at,goal;
static uint8_t searching,planned;

static uint16_t cell(uint8_t x,uint8_t y){return (uint16_t)y*20+x;}
static void pop_order(void){
    uint8_t i;
    for(i=1;i<queue_count;i++)orders[i-1]=orders[i];
    if(queue_count)--queue_count;
    planned=searching=work_ticks=0;path_length=path_at=0;
}
static void visit(uint16_t from,uint16_t next){
    if(walkable[next]&&parents[next]==65535){parents[next]=from;search[search_tail++]=next;}
}
static void begin_path(void){
    uint16_t i,start=cell(bram_x/8,bram_y/8);
    for(i=0;i<360;i++)parents[i]=65535;
    goal=cell(orders[0].x,orders[0].y);parents[start]=start;
    search[0]=start;search_head=0;search_tail=1;searching=1;planned=1;
}
static void search_step(void){
    uint8_t n=0,x,y;uint16_t a,b;
    while(search_head<search_tail&&n++<8){
        a=search[search_head++];
        if(a==goal){
            path_length=0;b=a;
            while(parents[b]!=b){path[path_length++]=b;b=parents[b];}
            path_at=path_length;searching=0;return;
        }
        x=a%20;y=a/20;
        if(x)visit(a,a-1);if(x<19)visit(a,a+1);
        if(y)visit(a,a-20);if(y<17)visit(a,a+20);
    }
    if(search_head==search_tail){rejected=30;pop_order();}
}
static void run_orders(void){
    uint8_t x,y;
    if(!queue_count)return;
    if(!planned){begin_path();return;}
    if(searching){search_step();return;}
    if(path_at){
        x=(path[path_at-1]%20)*8+4;y=(path[path_at-1]/20)*8+4;
        if(bram_x<x){++bram_x;facing=4;}
        else if(bram_x>x){--bram_x;facing=8;}
        else if(bram_y<y){++bram_y;facing=0;}
        else if(bram_y>y){--bram_y;facing=2;}
        if(bram_x==x&&bram_y==y)--path_at;
    }else if(orders[0].harvest&&!harvested){
        if(++work_ticks==60){harvested=1;loot=1;patch_pending|=1;resource_index=0;pop_order();}
    }else pop_order();
}
static void designate(void){
    uint8_t i,is_resource=cursor_x>=13&&cursor_x<=16&&cursor_y>=10&&cursor_y<=12;
    if(queue_count==8){rejected=30;return;}
    if(is_resource){
        if(harvested){rejected=30;return;}
        for(i=0;i<queue_count;i++)if(orders[i].harvest){rejected=30;return;}
        orders[queue_count].x=12;orders[queue_count].y=12;
    }else{
        if(!walkable[cell(cursor_x,cursor_y)]){rejected=30;return;}
        orders[queue_count].x=cursor_x;orders[queue_count].y=cursor_y;
    }
    orders[queue_count++].harvest=is_resource;
}
static void cursor_input(uint8_t keys,uint8_t pressed){
    uint8_t held=keys&(J_LEFT|J_RIGHT|J_UP|J_DOWN),dir=pressed&held;
    if(!dir)dir=(held&last_dir)?last_dir:held;
    dir=dir&J_LEFT?J_LEFT:dir&J_RIGHT?J_RIGHT:dir&J_UP?J_UP:dir&J_DOWN?J_DOWN:0;
    if(!dir){last_dir=repeat=0;return;}
    if(dir==last_dir&&repeat){--repeat;return;}
    repeat=dir==last_dir?3:7;last_dir=dir;
    if(dir==J_LEFT&&cursor_x)--cursor_x;
    if(dir==J_RIGHT&&cursor_x<19)++cursor_x;
    if(dir==J_UP&&cursor_y)--cursor_y;
    if(dir==J_DOWN&&cursor_y<17)++cursor_y;
}
static void pair(uint8_t obj,uint8_t tile,uint8_t x,uint8_t y,uint8_t prop){
    set_sprite_tile(obj,tile);set_sprite_prop(obj,prop);move_sprite(obj,x+8,y+16);
    set_sprite_tile(obj+1,tile+2);set_sprite_prop(obj+1,prop);move_sprite(obj+1,x+16,y+16);
}
static void draw_actors(void){
    uint8_t f=work_ticks?6+((frame_clock>>3)&1):(facing==8?4:facing)+(path_at?((frame_clock>>3)&1):0);
    uint8_t flip=facing==8?S_FLIPX:0,i;
    /* Swap the halves as well as their pixels when facing left. */
    for(i=0;i<4;i++){
        uint8_t half=i&1,layer=i>>1;
        set_sprite_tile(i,128+f*8+layer*4+(flip?(1-half):half)*2);
        set_sprite_prop(i,S_BANK|layer|flip);
        move_sprite(i,bram_x+half*8,bram_y);
    }
    pair(4,192,cursor_x*8-4,cursor_y*8-4,S_BANK|(rejected?3:2));
    /* Current order marker; just the top half of the hollow cursor. */
    if(queue_count){set_sprite_tile(6,192);set_sprite_prop(6,S_BANK|2);move_sprite(6,orders[0].x*8+8,orders[0].y*8+12);}
    else move_sprite(6,0,0);
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
    gotoxy(1,7);printf("B  EXPOSURE VIEW");
    gotoxy(1,9);printf("SELECT  RESET ROOM");
    gotoxy(1,11);printf("START  VIEW OR HELP");
    gotoxy(1,13);printf("BAG %u  ORDERS %u",loot,queue_count);
    gotoxy(1,15);printf("ISOLATED TEST");
    gotoxy(1,16);printf("NO SAVE OR AUDIO");
    vsync();set_bkg_palette(0,1,ui);SHOW_BKG;
}
static void show_room(void){
    uint8_t i;
    prepare();LCDC_REG|=LCDCF_BG8000;hicolor_menu_enabled=0;
    /* Load under black, retain the renderer's palette pointer but defer its ISR
     * until sprites and persistent state patches are also ready. */
    CRITICAL { hicolor_start(&master_data,2); hicolor_stop(); }
    for(i=0;i<12;i++)patch_tile(resource_ids[i],(harvested?resource_cut:resource_full)+i*16);
    for(i=0;i<10;i++)patch_tile(reveal_ids[i],(exposure?reveal_on:reveal_off)+i*16);
    VBK_REG=1;set_sprite_data(128,64,bram_tiles);set_sprite_data(192,4,cursor_tiles);VBK_REG=0;
    set_sprite_palette(0,2,actor_palettes);set_sprite_palette(2,2,cursor_palettes);
    patch_pending=resource_index=reveal_index=0;draw_actors();SHOW_BKG;SHOW_SPRITES;
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
        update_patch();cursor_input(keys,pressed);
        if(pressed&J_A)designate();
        if((pressed&J_B)&&!patch_pending){exposure=!exposure;patch_pending=2;reveal_index=0;}
        if(pressed&J_SELECT){
            queue_count=planned=searching=work_ticks=harvested=loot=exposure=0;
            path_at=path_length=0;patch_pending=3;resource_index=reveal_index=0;bram_x=44;bram_y=100;
        }
        /* Logic may resume after the long LCD ISR; no hardware writes here
         * except shadow OAM, which the next VBlank transfers. */
        run_orders();if(rejected)--rejected;draw_actors();
    }
}

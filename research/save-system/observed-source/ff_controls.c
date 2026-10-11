#pragma bank 255
#include <gbdk/platform.h>
#include "vm.h"
#include "actor.h"
#include "input.h"
#include "game_time.h"
#include "ff_routes.h"

#define QUEUE_CAPACITY 16
#define VALUE(n) (*(UWORD *)VM_REF_TO_PTR(-(n)-1))
#define OUTPUT(n) (script_memory[VALUE(n)])
typedef struct { UBYTE kind, target, x, y; } ff_order;
static ff_order orders[QUEUE_CAPACITY];
static UBYTE count, active, closed, last_direction, last_buttons, last_cursor_frame, cursor_delay;

static UWORD cell(UWORD x, UWORD y) {
    if (x >= 31 || y >= 28) return 65535;
    return ff_cells[y*32+x];
}

/* Args: op, kind, target, closed, result, state, targetID, type, y, x.
 * Results: 1 added, 2 cancelled, 3 full, 4 talk barrier, 5 active, 0 blocked.
 * Step states: 0 idle, 1 move one terrain-safe tile, 2 arrived.
 */
void ff_controls(SCRIPT_CTX *THIS) OLDCALL BANKED {
    UBYTE op = VALUE(0), kind = VALUE(1), target = VALUE(2);
    UBYTE i, direction, now, elapsed, held, pressed;
    UWORD start, goal, x, y;
    if (op == 0) {
        count = active = closed = last_direction = last_buttons = 0;
        cursor_delay = 0;
        OUTPUT(3) = 0;
        return;
    }
    if (op == 1) {
        /* Input overrides mask frame_joy before VM scripts run. Read the sampled
         * physical pad so the cursor stays independent of top-down movement. */
        held = joypads.joy0 & INPUT_DPAD;
        pressed = held & ~last_buttons;
        last_buttons = held;
        direction = pressed ? pressed : ((held & last_direction) ? last_direction : held);
        direction = (direction & J_LEFT) ? J_LEFT : (direction & J_RIGHT) ? J_RIGHT :
                    (direction & J_UP) ? J_UP : (direction & J_DOWN) ? J_DOWN : 0;
        now = (UBYTE)game_time;
        if (!direction) { last_direction = 0; return; }
        elapsed = now - last_cursor_frame;
        if (direction == last_direction && elapsed < cursor_delay) return;
        cursor_delay = direction != last_direction ? 8 : 4;
        last_direction = direction;
        last_cursor_frame = now;
        x = PLAYER.pos.x >> 8; y = PLAYER.pos.y >> 8;
        if (direction == J_LEFT && x > 0) --x;
        if (direction == J_RIGHT && x < 30) ++x;
        if (direction == J_UP && y > 1) --y;
        if (direction == J_DOWN && y < 27) ++y;
        PLAYER.pos.x = x << 8; PLAYER.pos.y = y << 8;
        return;
    }
    if (op == 2) {
        OUTPUT(4) = 0;
        if (closed) { OUTPUT(4) = 4; return; }
        x = OUTPUT(9); y = OUTPUT(8);
        if (cell(x,y) == 65535) return;
        if (kind == 1 || kind == 4) {
            for (i=0;i<count;++i) {
                if (orders[i].kind == kind && orders[i].target == target) {
                    if (kind == 4 || (i == 0 && active)) { OUTPUT(4) = 5; return; }
                    for (;i+1<count;++i) orders[i] = orders[i+1];
                    --count; OUTPUT(4) = 2; return;
                }
            }
        }
        if (count == QUEUE_CAPACITY) { OUTPUT(4) = 3; return; }
        orders[count].kind=kind; orders[count].target=target;
        orders[count].x=x; orders[count].y=y;
        ++count;
        if (kind == 3 || kind == 5) closed = 1;
        OUTPUT(3) = closed; OUTPUT(4) = 1;
        return;
    }
    if (op == 4) {
        if (count) {
            if (orders[0].kind == 3 || orders[0].kind == 5) closed = 0;
            for (i=0;i+1<count;++i) orders[i]=orders[i+1];
            --count;
        }
        active=0; OUTPUT(3)=closed;
        return;
    }
    OUTPUT(5)=0;
    if (!count) return;
    active=1;
    OUTPUT(6)=orders[0].target; OUTPUT(7)=orders[0].kind;
    x=OUTPUT(9); y=OUTPUT(8);
    start=cell(x,y); goal=cell(orders[0].x,orders[0].y);
    if (start == 65535 || goal == 65535) return;
    if (start == goal) { OUTPUT(5)=2; return; }
    direction=ff_direction(start,goal);
    if (direction==0) ++x;
    else if (direction==1) --x;
    else if (direction==2) ++y;
    else --y;
    OUTPUT(9)=x; OUTPUT(8)=y; OUTPUT(5)=1;
}

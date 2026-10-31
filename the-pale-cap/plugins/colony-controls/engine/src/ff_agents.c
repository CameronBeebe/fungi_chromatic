#pragma bank 255
#include "ff_agents.h"
#include "ff_routes.h"
#include "vm.h"

static const UBYTE cap_x[8] = {10,20,24,27,21,7,8,22};
static const UBYTE cap_y[8] = {23,21,19,16,13,12,7,7};
static UWORD distance(UWORD x, UWORD y, UWORD xx, UWORD yy) {
    return (x>xx?x-xx:xx-x)+(y>yy?y-yy:yy-y);
}
static UWORD cell(UWORD x, UWORD y) {
    return x<31 && y<28 ? ff_cells[y*32+x] : 65535;
}
static void changed(ff_agent *a) { if (++a->revision == 0) a->revision=1; }
static void release(ff_agent *a, ff_agent_world *w, UBYTE slot) {
    if(a->target && a->target<=8 && w->caps[a->target-1]==4+slot)
        w->caps[a->target-1]=0;
    a->target=a->progress=0;
}
static UBYTE near_bram(ff_agent *a, ff_agent_world *w) {
    return distance(a->x,a->y,w->bram_x,w->bram_y)<=2;
}
static UBYTE share(ff_agent *a, ff_agent_world *w) {
    if(!a->bag || w->fungi>=999 || !near_bram(a,w)) return 0;
    --a->bag; ++w->fungi;
    if(a->shared<999) ++a->shared;
    changed(a); return 4;
}
UBYTE ff_agent_command(ff_agent *a, ff_agent_world *w, UBYTE slot, UBYTE command) {
    if(slot>=FF_AGENT_COUNT || !a->initialized) return 0;
    if(command==4) return share(a,w);
    if(command==7) {
        if(!near_bram(a,w) || !w->fungi || a->bag>=FF_AGENT_BAG_MAX) return 0;
        --w->fungi; ++a->bag;
        if(a->trust<3) ++a->trust;
        if(a->gifts<999) ++a->gifts;
        changed(a); return 5;
    }
    if(command<1 || command>6) return 0;
    if(command==1 && !a->joined) return 0;
    if(command==5 && !near_bram(a,w)) return 0;
    release(a,w,slot);
    if(command==5) a->joined=1;
    if(command==6) a->joined=0;
    a->intent=(command==1 || command==5)?FF_AGENT_FOLLOW:
              (command==2 || command==6)?FF_AGENT_FORAGE:FF_AGENT_WAIT;
    changed(a); return 1;
}
static UBYTE move(ff_agent *a, ff_agent_world *w, UWORD x, UWORD y) {
    UWORD start=cell(a->x,a->y), goal=cell(x,y), nx=a->x, ny=a->y;
    UBYTE direction;
    if(start==65535 || goal==65535 || start==goal) return 0;
    direction=ff_direction(start,goal);
    if(direction==0) ++nx; else if(direction==1) --nx;
    else if(direction==2) ++ny; else --ny;
    if(cell(nx,ny)==65535 || (nx==w->bram_x && ny==w->bram_y)) return 0;
    a->x=nx; a->y=ny; return 2;
}
UBYTE ff_agent_step(ff_agent *a, ff_agent_world *w, UBYTE slot) {
    UBYTE i, best=255;
    UWORD d, closest=65535;
    if(slot>=FF_AGENT_COUNT || !a->initialized) return 0;
    if(a->intent==FF_AGENT_WAIT) return 0;
    /* Trust changes a real resource choice: friends keep one, strangers two. */
    if(a->joined && a->bag>(a->trust>=2?1:2) && near_bram(a,w)) return share(a,w);
    if(a->intent==FF_AGENT_FOLLOW)
        return near_bram(a,w)?0:move(a,w,w->bram_x,w->bram_y);
    if(a->bag>=FF_AGENT_BAG_MAX) {
        release(a,w,slot);
        return a->joined && !near_bram(a,w)?move(a,w,w->bram_x,w->bram_y):0;
    }
    if(a->target && (a->target>8 || w->caps[a->target-1]!=4+slot)) release(a,w,slot);
    if(!a->target) {
        for(i=0;i<8;++i) {
            d=distance(a->x,a->y,cap_x[i],cap_y[i]);
            if(!w->caps[i] && d<=FF_AGENT_SIGHT && d<closest) {best=i;closest=d;}
        }
        if(best==255)
            return a->joined && !near_bram(a,w)?move(a,w,w->bram_x,w->bram_y):0;
        a->target=best+1; w->caps[best]=4+slot; changed(a);
    }
    i=a->target-1;
    if(a->x!=cap_x[i] || a->y!=cap_y[i]) return move(a,w,cap_x[i],cap_y[i]);
    if(++a->progress<FF_AGENT_HARVEST_TICKS) return 0;
    w->caps[i]=3; ++a->bag; a->target=a->progress=0; changed(a); return 3;
}

#define VALUE(n) (*(UWORD *)VM_REF_TO_PTR(-(n)-1))
#define OUT(n) (script_memory[VALUE(n)])
/* op, slot, command, followed by addresses: state[12], world[11], result,
 * mailbox {slot, command, revision, sequence, consumed, status}.
 * Mailbox is transport-neutral. Producer writes sequence LAST. Applied once;
 * no remote mutation of position, resources, trust or memories is permitted.
 */
void ff_agents(SCRIPT_CTX *THIS) OLDCALL BANKED {
    ff_agent a; ff_agent_world w;
    UWORD *p=(UWORD *)&a, *q=(UWORD *)&w;
    UBYTE i, op=VALUE(0), slot=VALUE(1), result=0;
    if(slot>=FF_AGENT_COUNT) return;
    for(i=0;i<FF_AGENT_FIELDS;++i) p[i]=OUT(3+i);
    for(i=0;i<11;++i) q[i]=OUT(15+i);
    if(op==0 && !a.initialized) {
        a.x=slot?8:24; a.y=slot?12:14; a.intent=FF_AGENT_FORAGE;
        a.bag=0; a.trust=1; a.gifts=a.shared=0; a.revision=1;
        a.target=a.progress=0; a.joined=slot?0:1; a.initialized=1;
    }
    if(op==1) {
        if(OUT(27)==slot && OUT(30)!=OUT(31)) {
            if(OUT(30)>OUT(31) && OUT(29)==a.revision && OUT(28)>=1 && OUT(28)<=6) {
                result=ff_agent_command(&a,&w,slot,(UBYTE)OUT(28));
                OUT(32)=result?1:3;
            } else OUT(32)=2;
            /* Keep a high-water mark: old packets cannot reopen replay windows. */
            if(OUT(30)>OUT(31)) OUT(31)=OUT(30);
        }
        result=ff_agent_step(&a,&w,slot);
    }
    if(op==3) {release(&a,&w,slot);changed(&a);}
    if(op==2) result=ff_agent_command(&a,&w,slot,(UBYTE)VALUE(2));
    for(i=0;i<FF_AGENT_FIELDS;++i) OUT(3+i)=p[i];
    for(i=0;i<11;++i) OUT(15+i)=q[i];
    OUT(26)=result;
}

"""Compile the real agent runtime and real terrain routes; no model or emulator."""

from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
engine = root / "plugins/colony-controls/engine"
with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp)
    (p / "gbdk").mkdir()
    (p / "gbdk/platform.h").write_text(
        "#include <stdint.h>\ntypedef uint16_t UWORD; typedef uint8_t UBYTE;\n#define BANKED\n#define OLDCALL\n"
    )
    (p / "vm.h").write_text(
        "typedef struct {int unused;} SCRIPT_CTX;\nextern UWORD stack[33],script_memory[30];\n#define VM_REF_TO_PTR(i) (&stack[-(i)-1])\n"
    )
    (p / "test.c").write_text(
        """#include <assert.h>
#include <string.h>
#include "ff_agents.h"
UWORD stack[33],script_memory[30];
#include "SOURCE"
int main(void) {
 ff_agent a={24,14,2,0,1,0,0,1,0,0,1,1};
 ff_agent b={24,14,2,0,1,0,0,1,0,0,0,1};
 ff_agent_world w={25,13,0,{0}};
 unsigned i,total,harvested;
 // Both agents operate under identical code, with disjoint claims.
 ff_agent_step(&a,&w,0);ff_agent_step(&b,&w,1);
 assert(a.target && b.target && a.target!=b.target);
 assert(w.caps[a.target-1]==4 && w.caps[b.target-1]==5);
 // A changed intention releases only this agent's reservation.
 assert(ff_agent_command(&a,&w,0,3)==1 && !a.target);
 assert(w.caps[b.target-1]==5);
 // Player-reserved resources cannot be taken. Complete one actual harvest.
 for(i=0;i<8;i++)w.caps[i]=1;
 a.x=24;a.y=19;a.intent=2;w.caps[2]=0;
 for(i=0;i<FF_AGENT_HARVEST_TICKS;i++)ff_agent_step(&a,&w,0);
 assert(a.bag==1 && w.caps[2]==3 && !a.target);
 for(i=0;i<20;i++)ff_agent_step(&a,&w,0);
 assert(a.bag==1); // no duplicate harvest from a depleted patch
 // Gifts conserve inventory and alter future sharing reserves.
 a.x=24;a.y=14;w.fungi=3;total=a.bag+w.fungi;
 assert(ff_agent_command(&a,&w,0,7)==5 && a.trust==2 && a.gifts==1);
 assert(total==a.bag+w.fungi);
 ff_agent_step(&a,&w,0);assert(a.shared==1 && a.bag==1);
 assert(total==a.bag+w.fungi);
 w.fungi=999;assert(ff_agent_command(&a,&w,0,4)==0);
 a.bag=9;assert(ff_agent_command(&a,&w,0,7)==0);
 a.x=7;a.y=12;assert(ff_agent_command(&a,&w,0,7)==0);
 assert(ff_agent_command(&a,&w,0,5)==0);
 // Terrain-safe following crosses real route fields, stopping by Bram.
 a.intent=1;a.bag=0;
 for(i=0;i<200;i++){ff_agent_step(&a,&w,0);assert(cell(a.x,a.y)!=65535);}
 assert(distance(a.x,a.y,w.bram_x,w.bram_y)<=2);
 // VM bridge: unknown slot, stale revisions and replay never mutate inventory.
 for(i=0;i<30;i++)stack[3+i]=i;
 stack[0]=0;stack[1]=0;ff_agents(0);
 script_memory[12]=25;script_memory[13]=13;
 script_memory[24]=0;script_memory[25]=3;script_memory[26]=script_memory[7];
 script_memory[27]=1;stack[0]=1;ff_agents(0);
 assert(script_memory[2]==0 && script_memory[28]==1 && script_memory[29]==1);
 script_memory[25]=2;ff_agents(0);assert(script_memory[2]==0);
 script_memory[27]=2;script_memory[26]=0;ff_agents(0);
 assert(script_memory[2]==0 && script_memory[29]==2 && script_memory[28]==2);
 script_memory[27]=1;ff_agents(0);assert(script_memory[28]==2);
 script_memory[27]=3;script_memory[26]=script_memory[7];script_memory[25]=7;ff_agents(0);
 assert(script_memory[29]==2); // remote may not spend player's inventory
 // Long simulation conserves resources across two autonomous agents.
 memset(&w,0,sizeof(w));w.bram_x=25;w.bram_y=13;
 a=(ff_agent){24,14,2,0,1,0,0,1,0,0,1,1};
 b=(ff_agent){8,12,2,0,1,0,0,1,0,0,0,1};
 for(i=0;i<1000;i++){ff_agent_step(&a,&w,0);ff_agent_step(&b,&w,1);}
 harvested=0;for(i=0;i<8;i++)if(w.caps[i]==3)++harvested;
 assert(harvested>1 && harvested==a.bag+b.bag+w.fungi);
 return 0;
}
""".replace(
            "SOURCE", str(engine / "src/ff_agents.c")
        )
    )
    subprocess.run(
        [
            "cc",
            "-Wno-unknown-pragmas",
            "-I",
            tmp,
            "-I",
            str(engine / "include"),
            str(p / "test.c"),
            *[str(engine / f"src/ff_routes_{i}.c") for i in range(3)],
            "-o",
            str(p / "test"),
        ],
        check=True,
    )
    subprocess.run([str(p / "test")], check=True)
    (p / "actor.h").write_text(
        "typedef struct {struct {UWORD x,y;} pos;} actor_t;\nextern actor_t player;\n#define PLAYER player\n"
    )
    (p / "input.h").write_text(
        "#define INPUT_DPAD 15\n#define J_RIGHT 1\n#define J_LEFT 2\n#define J_UP 4\n#define J_DOWN 8\ntypedef struct {UBYTE joy0;} joypads_t;\nextern joypads_t joypads;\n"
    )
    (p / "game_time.h").write_text("extern UWORD game_time;\n")
    (p / "cursor.c").write_text(
        """#include <assert.h>
#include <gbdk/platform.h>
UWORD stack[33], script_memory[30], game_time;
#include "SOURCE"
actor_t player; joypads_t joypads;
int main(void) {
 unsigned i; player.pos.x=15<<8;player.pos.y=22<<8;
 // Four queued press edges survive release before the native handler runs.
 for(i=0;i<4;i++){game_time+=8;joypads.joy0=0;stack[0]=5;stack[1]=J_UP;ff_controls(0);}
 assert(player.pos.y==(18<<8));
 // Polling in the same frame cannot duplicate a captured press.
 joypads.joy0=J_UP;stack[0]=1;ff_controls(0);assert(player.pos.y==(18<<8));
 // Holding repeats only after the initial delay.
 game_time+=4;ff_controls(0);assert(player.pos.y==(18<<8));
 game_time+=4;ff_controls(0);assert(player.pos.y==(17<<8));
 return 0;
}
""".replace(
            "SOURCE", str(engine / "src/ff_controls.c")
        )
    )
    subprocess.run(
        [
            "cc",
            "-Wno-unknown-pragmas",
            "-I",
            tmp,
            str(p / "cursor.c"),
            *[str(engine / f"src/ff_routes_{i}.c") for i in range(3)],
            "-o",
            str(p / "cursor"),
        ],
        check=True,
    )
    subprocess.run([str(p / "cursor")], check=True)

print(
    "PASS: terrain, reservations, shared agent rules, inventory conservation, trust, stale/replayed remote decisions"
)

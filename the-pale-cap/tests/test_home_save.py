"""Native record implementation checks using a host SRAM adapter."""

from pathlib import Path
import subprocess, tempfile

root = Path(__file__).resolve().parents[1]
source = (root / "plugins/colony-controls/engine/src/ff_home_save.c").read_text()
with tempfile.TemporaryDirectory() as t:
    p = Path(t)
    (p / "gbdk").mkdir()
    (p / "gbdk/platform.h").write_text(
        """#include <stdint.h>
typedef uint16_t UWORD;
#define OLDCALL
#define BANKED
extern uint8_t banks[2][8192];
#define ENABLE_RAM
#define DISABLE_RAM
#define SWITCH_RAM(n) (ram=banks[n])
"""
    )
    (p / "vm.h").write_text(
        "typedef struct {int unused;} SCRIPT_CTX;\nextern UWORD stack[46],script_memory[45];\n#define VM_REF_TO_PTR(i) (&stack[-(i)-1])\n"
    )
    source = source.replace("(volatile uint8_t *)0xa000", "banks[0]")
    (p / "save.c").write_text(source)
    (p / "test.c").write_text(
        """#include <assert.h>
#include <string.h>
#include <stdint.h>
uint8_t banks[2][8192];uint16_t stack[46],script_memory[45];
#include "save.c"
static void op(int n){int i;stack[0]=n;stack[1]=44;for(i=0;i<44;i++)stack[i+2]=i;ff_home_save(0);}
int main(void){uint8_t a[SIZE],b[SIZE];int k;
 op(0);assert(script_memory[44]==0);
 script_memory[17]=1;script_memory[18]=1;script_memory[19]=7;
 script_memory[23]=4;script_memory[24]=2;script_memory[25]=3;script_memory[26]=1;script_memory[31]=1;
 op(2);assert(script_memory[44]==1);memcpy(a,banks[0],SIZE);
 script_memory[19]=9;op(2);assert(script_memory[44]==1);memcpy(b,banks[1],SIZE);
 memset(script_memory,0,sizeof(script_memory));op(1);assert(script_memory[17]==1&&script_memory[18]==1&&script_memory[19]==9);
 assert(script_memory[23]==4&&script_memory[24]==2&&script_memory[25]==3&&script_memory[26]==1);
 // Every interrupted prefix before the final commit must recover previous A.
 for(k=0;k<SIZE;k++){memset(banks[1],0,SIZE);memcpy(banks[1],b,k);banks[1][SIZE-1]=0;op(1);assert(script_memory[19]==7&&script_memory[44]==1);}
 // Damage every byte of the newest record, including checksum and commit.
 for(k=0;k<SIZE;k++){memcpy(banks[1],b,SIZE);banks[1][k]^=1;op(1);assert(script_memory[19]==7);}
 memcpy(banks[1],b,SIZE);banks[0][0]^=1;op(1);assert(script_memory[19]==9);
 banks[1][0]^=1;op(0);assert(script_memory[44]==3);
 memset(banks,255,sizeof(banks));op(0);assert(script_memory[44]==0);
 // Invalid ownership cannot be committed.
 script_memory[17]=2;script_memory[18]=1;op(2);assert(script_memory[44]==2);
 // Version 1 records still load, and initialize new agent records as empty.
 memset(banks,0,sizeof(banks));memset(record,0,SIZE);
 record[0]='P';record[1]='C';record[2]='H';record[3]='1';record[4]=1;record[5]=20;
 record[12+19*2]=42;{uint16_t c=crc(record,52);record[52]=c;record[53]=c>>8;record[54]=0xa5;}
 memcpy(banks[0],record,55);op(1);assert(script_memory[19]==42&&script_memory[44]==1);
 for(k=20;k<44;k++)assert(script_memory[k]==0);
 // A home record cannot contain an active harvest reservation.
 script_memory[28]=1;op(2);assert(script_memory[44]==2);
 return 0;}
"""
    )
    subprocess.run(
        ["cc", "-Wno-unknown-pragmas", "-I", t, str(p / "test.c"), "-o", str(p / "test")],
        check=True,
    )
    subprocess.run([str(p / "test")], check=True)
print(
    "PASS: record roundtrip, 103 interrupted prefixes, 103 corruptions, agent memory, v1 migration, fallback, empty and invalid ownership"
)

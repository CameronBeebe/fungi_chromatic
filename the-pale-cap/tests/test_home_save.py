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
        "typedef struct {int unused;} SCRIPT_CTX;\nextern UWORD stack[22],script_memory[21];\n#define VM_REF_TO_PTR(i) (&stack[-(i)-1])\n"
    )
    source = source.replace("(volatile uint8_t *)0xa000", "banks[0]")
    (p / "save.c").write_text(source)
    (p / "test.c").write_text(
        """#include <assert.h>
#include <string.h>
#include <stdint.h>
uint8_t banks[2][8192];uint16_t stack[22],script_memory[21];
#include "save.c"
static void op(int n){int i;stack[0]=n;stack[1]=20;for(i=0;i<20;i++)stack[i+2]=i;ff_home_save(0);}
int main(void){uint8_t a[55],b[55];int k;
 op(0);assert(script_memory[20]==0);
 script_memory[17]=1;script_memory[18]=1;script_memory[19]=7;
 op(2);assert(script_memory[20]==1);memcpy(a,banks[0],55);
 script_memory[19]=9;op(2);assert(script_memory[20]==1);memcpy(b,banks[1],55);
 memset(script_memory,0,sizeof(script_memory));op(1);assert(script_memory[17]==1&&script_memory[18]==1&&script_memory[19]==9);
 // Every interrupted prefix before the final commit must recover previous A.
 for(k=0;k<=54;k++){memset(banks[1],0,55);memcpy(banks[1],b,k);banks[1][54]=0;op(1);assert(script_memory[19]==7&&script_memory[20]==1);}
 // Damage every byte of the newest record, including checksum and commit.
 for(k=0;k<55;k++){memcpy(banks[1],b,55);banks[1][k]^=1;op(1);assert(script_memory[19]==7);}
 memcpy(banks[1],b,55);banks[0][0]^=1;op(1);assert(script_memory[19]==9);
 banks[1][0]^=1;op(0);assert(script_memory[20]==3);
 memset(banks,255,sizeof(banks));op(0);assert(script_memory[20]==0);
 // Invalid ownership cannot be committed.
 script_memory[17]=2;script_memory[18]=1;op(2);assert(script_memory[20]==2);
 return 0;}
"""
    )
    subprocess.run(
        ["cc", "-Wno-unknown-pragmas", "-I", t, str(p / "test.c"), "-o", str(p / "test")],
        check=True,
    )
    subprocess.run([str(p / "test")], check=True)
print(
    "PASS: record roundtrip, 55 interrupted prefixes, 55 corruptions, fallback, empty and invalid ownership"
)

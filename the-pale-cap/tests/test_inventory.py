"""Exercise the actual native transfer code with a minimal host VM adapter."""

from pathlib import Path
import subprocess, tempfile

root = Path(__file__).resolve().parents[1]
source = root / "plugins/colony-controls/engine/src/ff_inventory.c"
with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp)
    (p / "gbdk").mkdir()
    (p / "gbdk/platform.h").write_text(
        "typedef unsigned short UWORD;\n#define OLDCALL\n#define BANKED\n"
    )
    (p / "vm.h").write_text(
        "typedef struct { int unused; } SCRIPT_CTX;\nextern UWORD stack[5], script_memory[4];\n#define VM_REF_TO_PTR(i) (&stack[-(i)-1])\n"
    )
    (p / "test.c").write_text(
        """#include <assert.h>
#include <gbdk/platform.h>
UWORD stack[5], script_memory[4];
#include "SOURCE"
static void op(int n) { stack[0]=n; stack[1]=0; stack[2]=1; stack[3]=2; stack[4]=3; ff_inventory(0); }
int main(void) {
 script_memory[1]=1; script_memory[3]=7;
 op(2); assert(script_memory[0]==1);
 op(0); assert(script_memory[0]==0 && script_memory[1]==2 && script_memory[2]==7 && script_memory[3]==0);
 op(0); assert(script_memory[1]==2 && script_memory[2]==7);
 op(2); assert(script_memory[0]==0);
 op(1); op(1); assert(script_memory[1]==1);
 op(3); assert(script_memory[2]==0 && script_memory[3]==7);
 op(3); assert(script_memory[3]==7);
 script_memory[2]=995; script_memory[3]=10;
 op(0); assert(script_memory[2]==999 && script_memory[3]==6);
 op(3); assert(script_memory[3]==999 && script_memory[2]==6);
 script_memory[2]=1001; script_memory[3]=10;
 op(0); assert(script_memory[2]==1001 && script_memory[3]==10);
 script_memory[1]=0; script_memory[0]=0; op(1); op(2); assert(script_memory[1]==0 && script_memory[0]==0);
 return 0;
}
""".replace(
            "SOURCE", str(source)
        )
    )
    subprocess.run(
        ["cc", "-Wno-unknown-pragmas", "-I", tmp, str(p / "test.c"), "-o", str(p / "test")],
        check=True,
    )
    subprocess.run([str(p / "test")], check=True)
print("PASS: ownership, repeated transfers, equip guards, capacity and conservation")

#pragma bank 255
#include <gbdk/platform.h>
#include "vm.h"
#define VALUE(n) (*(UWORD *)VM_REF_TO_PTR(-(n)-1))
#define OUTPUT(n) (script_memory[VALUE(n)])
/* op, equipped, location, stored fungi, carried fungi. Stable instance #1. */
void ff_inventory(SCRIPT_CTX *THIS) OLDCALL BANKED {
    UWORD amount;
    switch (VALUE(0)) {
    case 0:
        if (OUTPUT(2) == 1) { OUTPUT(2) = 2; OUTPUT(1) = 0; }
        amount = OUTPUT(3) >= 999 ? 0 : 999 - OUTPUT(3);
        if (amount > OUTPUT(4)) amount = OUTPUT(4);
        OUTPUT(3) += amount; OUTPUT(4) -= amount;
        break;
    case 1:
        if (OUTPUT(2) == 2) OUTPUT(2) = 1;
        break;
    case 3:
        amount = OUTPUT(4) >= 999 ? 0 : 999 - OUTPUT(4);
        if (amount > OUTPUT(3)) amount = OUTPUT(3);
        OUTPUT(4) += amount; OUTPUT(3) -= amount;
        break;
    case 2:
        if (OUTPUT(2) == 1) OUTPUT(1) = !OUTPUT(1);
        break;
    }
}

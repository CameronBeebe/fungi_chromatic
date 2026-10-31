#ifndef FF_AGENTS_H
#define FF_AGENTS_H
#include <gbdk/platform.h>
#define FF_AGENT_COUNT 2
#define FF_AGENT_FIELDS 12
#define FF_AGENT_BAG_MAX 9
#define FF_AGENT_HARVEST_TICKS 6
#define FF_AGENT_SIGHT 6
#define FF_AGENT_WAIT 0
#define FF_AGENT_FOLLOW 1
#define FF_AGENT_FORAGE 2
/* Stable semantic record, mirrored to named GBVM variables. No VM pointers. */
typedef struct {
    UWORD x, y, intent, bag, trust, gifts, shared, revision;
    UWORD target, progress, joined, initialized;
} ff_agent;
typedef struct {
    UWORD bram_x, bram_y, fungi, caps[8];
} ff_agent_world;
/* Commands: 1 follow, 2 forage, 3 wait, 4 share, 5 join, 6 leave,
 * 7 player gives one fungus (local dialogue only).
 * Result: 0 unavailable, 1 accepted, 2 moved, 3 harvested, 4 shared, 5 gift.
 */
UBYTE ff_agent_command(ff_agent *a, ff_agent_world *w, UBYTE slot, UBYTE command);
UBYTE ff_agent_step(ff_agent *a, ff_agent_world *w, UBYTE slot);
#endif

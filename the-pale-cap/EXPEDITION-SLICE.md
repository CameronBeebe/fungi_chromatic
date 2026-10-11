# First expedition and hideout slice

October 11, 2026. Implementation proposal following the user's approved priority
order. Numbers and loss rules below are test defaults, not settled game canon.
No gameplay implementation is claimed by this document.

## The experience to prove

Leave a beautiful, useful home; discover an object worth inspecting; use it to
make a better gathering decision; bring the find back; change something at home.
One expedition map, one fork, one stash and one improvement are sufficient.
Keep existing artwork intact. New art remains separate until reviewed individually.

## First-session sequence

1. Start at home with an empty expedition bag. The exit shows what you carry.
2. Enter the existing expedition room with the cursor and autonomous dwarf.
3. Receive the authored fork from Luma through the queued conversation. Ground
   pickups can later use the same acquisition rules. Inspecting or receiving an
   item does not automatically equip it.
4. Equip from the inventory overlay. Use its pulse to discover a productive
   branch of the network, then designate gathering in real time.
5. Return to the entrance and choose Return home. Earlier orders finish before
   this final travel order; no later orders can be appended. Arrival opens a
   confirmation, rather than teleporting when the cursor touches the exit.
6. Deposit finds, retaining the exact fork. Spend gathered material to build a
   preparation shelf. On the next trip, the shelf supplies a small pulse reserve.

## Carrying and extraction

Test a six-slot expedition bag and twelve-slot home stash. Unique equipment takes
one slot; each resource type stacks to a bounded limit. Start with one resource
type. Capacity must be checked again when collection completes, since queued
jobs may fill the bag first. A rejected pickup remains in the world.

Returning home secures carried items; deposition is an explicit move between bag
and stash, not creation of a second copy. If the stash is full, keep excess in
the bag and allow return anyway. Leaving again exposes whatever remains carried.
Equipping references an item in the bag and does not free its slot.

Do not add death merely to demonstrate loss. First provide an explicit emergency
retreat option: show the exact carried items that will be abandoned, require
confirmation, return home, and preserve home storage and improvements. Treat this
as a provisional loss test until combat and escape rules exist. Normal exit has
no invented countdown or threat; acknowledge that real extraction tension will
need environmental or encounter pressure in a later pass.

Agreed revision: saving is possible only at the hideout, after extraction. There
are no mid-run saves or expedition-resume checkpoints. New Game starts at home.
When a valid compatible save exists, cartridge boot loads directly into the
hideout without a title menu or Continue prompt. With no save, show the startup
menu; New Game then enters home. Invalid/incompatible saves need explicit handling,
not silent replacement. A destructive New Game option belongs behind confirmation.

Quitting a run returns to the last hideout save and loses unsaved run progress.
Whether departure must record equipment at risk to enforce losses remains open;
do not quietly introduce that rule. Explicit saving versus autosaving at home
also remains to be decided. Queue serialization is unnecessary: finish the return
transaction, clear pending orders, and save only settled home state.

## Fork: one useful action

Working name Gillsong; current illustration and name remain concept candidates.
Proposed effect: pulse from the dwarf into the connected mycelial component,
briefly marking its resource-bearing endpoints. It does not harvest, teleport,
teach a word, or permanently change the dwarf's perception.

The choice is whether information is worth its resource cost before committing
travel and gathering time. Use one carried spore unit as the initial test cost.
Provide a small guaranteed source near the entrance so discovery cannot deadlock.
The preparation shelf supplies one pulse unit at departure, capped at one and
only refreshed after completing an expedition with newly gathered material.
This cap and completion rule prevent free accumulation by repeatedly crossing
the doorway. Exact cost and shelf benefit need testing, not additional stats.

Use is a queued dwarf action. Evaluate connectivity at execution, and deduct cost
only when a valid pulse starts. No network, missing equipment or insufficient
spores produces a short explanation without payment. Snapshot revealed endpoints
for the effect duration; subsequently collecting one removes its resource marker.
Do not repurpose B globally until its relationship to current spell casting is
decided. First expose Use in the inventory overlay as a functional test entry.

This overlaps with Reveal and must be compared directly: Reveal currently shows
network structure; the proposed fork locates useful endpoints. If that difference
does not change a player's decision, revise or discard the fork effect rather
than maintaining two near-identical abilities. Words/exposure/magic boundaries
remain open; this experiment does not settle their ontology.

## Home as an illustrated place

Use a fixed, composed room inspired by the atmosphere of classic illustrated
adventures and palette-driven environments. Candidate hotspots: stash, preparation
shelf and expedition entrance. Do not build cultivation, forge and trading menus
simultaneously. A stable room can later gain visible additions as it develops.

Create three separate concept directions before replacing art: a hollow-root
refuge, a mineral grotto workshop, and a sheltered fungal conservatory. Each
should give the entrance, storage and future construction an obvious visual home,
include a quiet area for readable overlays, and suggest one localized animated
feature. Evaluate at 160×144 before commissioning finished background tiles.

For the first functional test, use clearly labeled temporary hotspots. No concept
painting is automatically an approved production asset. Preserve the detailed
fork illustration for inspection; use a shared fork-family pickup/icon candidate.
Visible equipped gear, individual overworld variant sprites and color coding can
wait. Do not infer stats from illustration labels such as AMBER or WORN.

## Menus and controls

- Start: Bag / Return during expeditions; Bag / Stash / Save at home only. Inventory pauses simulation
  for this test; resume without elapsed-time catch-up.
- Bag: compact list with capacity, equipped marker and selected-item summary.
- Inspect: large artwork, implemented effect and cost; A opens a small action
  list, B returns. Avoid hiding equipping behind an unexplained close action.
- Item actions: Equip or Unequip, Use when applicable, Deposit when home.
- Select continues to serve the existing spell overview until explicitly revised.
- Home: D-pad moves among clearly indicated hotspots, A enters, B backs out.

Do not place inventory or spell selection in the dialogue box. Separate flavor
text from functional claims. Show only implemented properties; leave speculative
affinities and durability out of the first menu.

## Implementation boundaries

Persist schema version, stable item instance IDs, item definitions/imprints,
ownership location, equipment reference, collected world object IDs, resources,
home improvements, home dwarf state and learned knowledge. Do not persist an
active expedition checkpoint.
Every item must have exactly one owner/location. A view change cannot respawn a
collected object. Preserve intrinsic properties through every transfer.

The current native order queue uses static C storage outside ordinary script
variables. Do not serialize it. Complete extraction, clear pending work and any
queue barrier, and settle any reservations before saving at home. Boot restores
an idle dwarf at home. Never resume a half-paid harvest or stale talk barrier.

Implement persistent saves with version/checksum validation and a recoverable
previous record where cartridge storage permits. Confirm storage capacity and
existing engine save behavior before choosing record layout. A successful save
message requires successful persistence; never equate scene transition with save.

## Acceptance checks

- Collect, equip, use, return, deposit, reload: the same item and properties survive.
- Full bag leaves the pickup; full stash does not prevent safe return.
- Repeated deposit/withdraw/equip does not duplicate items or free capacity.
- Invalid or cancelled pulse does not spend resources; successful pulse spends once.
- A discovered endpoint helps choose a route that ordinary Reveal alone does not.
- Emergency retreat loses only the explicitly listed carried items.
- Save is unavailable during runs; cold boot with a valid save opens the hideout.
- Saved item identities, ownership, knowledge and improvements survive cold boot.
- No save shows startup options; corrupt/incompatible data is not silently discarded.
- Returning with queued jobs does not leave orders pointing into the previous scene.
- Menus freeze simulation consistently; closing does not fast-forward work.
- Shelf purchase charges once; its benefit cannot be farmed at the doorway.
- Test native screen readability and physical save/restart behavior separately.

## Deferred

Combat implementation, multi-axis affinities, generated items, link trading,
multiple biomes, expanded cultivation and visible equipment. Their design remains
valid; none is necessary to prove this first loop. The language encounter remains
in the backlog and must be revisited alongside the Reveal/fork distinction.

## Approved presentation direction — October 11

Use Vermilion from `art-tests/gillsong-refinement/01-vermilion.png` for the first
illustrated fork inspection. Approval is specific to this variant, not blanket
approval of other asset replacements. Preserve the source study.

General menus should follow the Gillsong dark/cyan language rather than the
current pale papyrus-like overlay: near-black blue/violet ground, cyan/blue
framing, warm pale text, and a distinct selected/equipped treatment. Use restrained
borders for lists; richer filigree belongs on inspection and special screens.
Keep contrast and text legibility at 160×144; do not animate ordinary menu text or
let decoration compete with selection. This is the target, not yet implemented UI.

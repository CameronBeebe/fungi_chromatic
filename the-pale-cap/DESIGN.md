# The Pale Cap — design

A psychedelic real-time strategy looter extraction game: direct a dwarf's work,
gather useful discoveries, alter perception and bring finds back to a persistent
hideout. This is the design target; the implemented game is a small offline slice.
[README.md](README.md) describes controls and current behavior, and
[PLAYTEST.md](PLAYTEST.md) separates hardware observations from automated evidence.

## Core rules

- The cursor issues orders; Bram walks and works independently. The cursor is an
  interface, not another character. Attractive environments must still support
  legible targets, reachable work and useful queued actions.
- The played dwarf's spore exposure determines the player's perception. There is
  no separate cursor/player meter or colony-wide exposure pool. Other characters
  can eventually perceive different things.
- Perceptual changes reveal views of one persistent world. They do not refresh
  resources, duplicate items or erase completed work.
- Gathering and spending must have consequences. Spores are desirable resources
  that can affect cognition, access and abilities, not simply a poison meter.
- The cartridge is offline and deterministic. Models may author content during
  development; networking does not belong in the runtime order loop.

## Implemented in the integrated cartridge

Bram follows precomputed routes and a bounded 16-order FIFO. A queues movement,
harvesting or conversation; a conversation waits for earlier work and closes
admission until it finishes. Pending harvests can be cancelled. Rewards arrive
at completion, and independent resource states prevent repeated-input rewards.
Menus and dialogue pause work. Routes currently ignore character collisions.

Bloom spends fungi to awaken a root and later regrow its harvested patches.
Reveal animates a connected mycelial overlay and exposes an authored encounter
once all three roots are awake. Harvesting increases scalar exposure, which
influences Reveal duration/signals. Spells currently execute immediately at the
cursor; range, queued casting and proximity/decay rules are unresolved.

The hideout supports departure, queued return/extraction, bag/stash transfers,
inspection, equipment and saving. Luma grants one authored Gillsong fork. Its
active ability is pending. The Hearth uses a cropped Hi-Color scene above home
menus; inspection uses the Vermilion study with animated cyan ornament.

### Save and ownership invariants

- Save only at home after extraction; no mid-run resume.
- A valid compatible save boots into the hideout. Without one, startup offers
  New Game/Controls; New Game begins at home.
- Save settled state, not queued work or live script continuations. Restore an
  idle dwarf. Invalid/incompatible records must not be silently overwritten.
- Item collection, transfer and equipment mutations preserve ownership and
  resource conservation. No duplicate harvest, pickup, extraction or transfer.
- Quitting a run returns to the last home save. Departure records, equipment
  loss and autosave timing still need an explicit design decision.

## Visual and conceptual direction

Fungal ecology supplies hyphae, mycelium, spores, sclerotia, flushes, substrates
and distinct biomes. These are an evocative gameplay vocabulary, not a claim of
biological simulation. Beauty on the Chromatic screen is a core priority.

Dune's spice suggests a resource economy linked to awareness; McKenna's language
and strange intelligences suggest communication with unfamiliar beings;
Psychonauts suggests perceptual environments; dwarf simulation supplies autonomous
work. Pokémon suggests legible affinities, collection, exchange and encounter
pacing. These are influences for an original setting, not feature checklists.

Language should change what can be understood or done, and potentially how the
world looks or how its objects are categorized. Exposure, learned words and magic
can all affect perception, but their roles need a focused playtest before adding
three overlapping progression systems. Ordinary perception need not be the
privileged truth. Keep targets readable; psychedelic atmosphere is more than
full-screen flicker.

One candidate encounter, **The Unfinished Word**, teaches a sign through a being's
repeated gesture and a visible consequence. A working gloss, JOIN, could connect
either a productive bed or a spore-rich branch. Knowledge and established links
would persist after exposure fades. This is a proposal, not implemented content;
it must not restrict all future language mechanics to verbs or password puzzles.

## Intended expedition and item systems

Prepare at home → enter a biome → gather and shape perception → choose what to
carry → extract → store, equip, cultivate, build or trade. The hideout should
become a place to personalize, with a few useful stations before broad crafting.
Run failure, retreat loss, carrying limits and stabilization rules remain open.

A view may reveal unique discoveries or different opportunities in the same
core. Underlying object identities persist across views. Distinguish perception
changes from actual world mutations and permanently recorded discoveries.

Items need a bounded vocabulary of implemented effects, conditions, costs,
targets and limits. A generated description or valid schema alone does not make
an item functional, interesting or balanced. Start with a few satisfying effects.

### Stable properties, changing usefulness

Persist instance identity, intrinsic stats, origin/imprint and mutable wear.
Derive effective behavior from current perception, equipment and knowledge.
Trading preserves intrinsic properties and wear; the recipient can experience
different effective strengths. Switching views must not reroll, duplicate or
repair an item without an explicit mechanic. Equipment that changes perception
needs a deterministic evaluation order to prevent feedback loops/bonus stacking.

Exposure may eventually become a spectrum of fungal influences rather than one
scalar. Polypore/bolete-like affinities and fictional influences are exploratory
labels. An item's recorded imprint can reflect its origin or discovery conditions
and outlast the trip. The imprint moment and formulas are undecided. A dimension
ID can identify provenance without requiring a separately simulated universe.

Trade discovery could rank another inventory by spectrum resonance and practical
usefulness, showing a few recommendations with explanations. Similarity alone is
not usefulness: equipment gaps, planned exploration, costs and tradeoffs matter.
Avoid excessive poorly defined stats that turn most drops into junk.

### Encounters and trading

Turn-based fights are the intended combat experiment, with the exploration world
paused during the encounter and resumed afterward. Do not accidentally advance
harvests, exposure timers or hazards while battle menus are open. This is not yet
implemented, nor does it imply automated fights or creature collecting.

Link-cable trading is planned independently of Wi-Fi/model services. It needs
compatible item schemas, mutual confirmation, capacity checks, interrupted
transfer recovery and save integrity. Hardware/protocol support remains research.

## Scene authoring and runtime boundary

The current two-model pipeline reads decoded native pixels plus creative intent,
proposes objects/descriptions, and judges labels, bounds, relations and changes.
Human review corrects geometry and mechanics. Exact pixel/tile checks and code
validate budgets, reachability, costs and supported effects.

The review-to-ROM adapter now builds a standalone one-room Heartwood harness
with one fixed harvest patch. It does **not** feed the integrated game's scene
or plugin data yet. Full-image and cropped object bounds can disagree; neither
becomes collision by confidence alone. See [SCENE-GENERATION.md](SCENE-GENERATION.md).

Production scenes should share a master pixel image, fixed palette schedule and
bounded patches for harvest/reveal states. Sprites must fit the background's
palette, scale and light. Walkable space, work positions, layering and interaction
states are authored data alongside the art, not inferred during cartridge play.
Detailed inspection and fixed hideout screens can carry more visual richness than
small overworld item icons; visible equipment is not required yet.

## Next slice

Extend the reviewed contract to another scene and several useful interactions,
then connect it to extraction and existing home persistence. Validate the complete
loop before expanding item schemas or generating many levels. Keep hardware
readability, route correctness, feedback and resource conservation measurable.

See [TODO.md](TODO.md) for open work and [EXPEDITION-SLICE.md](EXPEDITION-SLICE.md)
for the detailed expedition proposal, including provisional values. Earlier
reasoning is retained in [design history](../docs/notes/design-history.md).

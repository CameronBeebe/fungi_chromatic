# The Pale Cap — living TODO

Updated October 10, 2026. This is the GBC adaptation's backlog; the terminal
repository keeps its own TODO. The order below is a recommendation, not a set
of settled design decisions. Keep experiments small and playable, update this
file after each pass, and record verified behavior in PLAYTEST.md.

## Design anchors

- Identity: psychedelic real-time strategy looter extraction.
- Build a persistent hideout; bring discoveries home to keep, use, cultivate or trade.
- Link-cable item trading is desired; implementation and hardware support need research.
- Fungal ecology (hyphae, sclerotia, spores, flushes) and distinct biomes guide art and play.
- Visual beauty on the Chromatic is a core priority in its own right.
- Learned language can reshape appearance and perceived categories of the same world.

- Cursor issues orders to the played dwarf; the dwarf performs the work.
- The played dwarf's spore exposure determines the player's view. The cursor
  has no separate exposure, and exposure is not colony-wide.
- Perceptual changes reveal different views of a persistent physical world.
- Real-time gathering, resource spending, mycelial systems and character
  encounters are the core. Conventional combat is optional.
- Language should unlock understanding or action, beyond decorative glyphs.
- Spores are desirable resources affecting cognition, perception and abilities.
- MVP is offline. Live LLM/Jev generation and proposed Wi-Fi/firmware work are later.
- Current controls, queue policy, spell costs and progression are experiments.

## Current priorities (user direction, October 10)

### Priority 1. Establish visual direction with concept art and native assets

- [ ] Explore a small set of original concept directions for fungal architecture,
  desirable spore materials, dwarf equipment and language-bearing intelligences.
- [ ] Show the SAME place at ordinary and elevated exposure; retain recognizable
  geography while changing what can be perceived and understood.
- [ ] Develop Bram, one encounter entity and one landmark together, with clear
  silhouettes, scale, palette relationships and expressive animation ideas.
- [ ] Include language emerging from gesture, anatomy and environmental patterns;
  avoid treating every strange being as a generic glowing humanoid.
- [ ] Translate the chosen direction into actual-size GBC sprite/tile studies,
  then idle, movement and communication cels. Concept paintings are direction,
  not automatically cartridge-ready assets.
- [ ] Produce one cohesive encounter-room mockup before expanding the asset set.
- [ ] Explore a buildable hideout and one contrasting expedition biome, including
  hyphae, sclerotia, spores and flushes with distinct visual identities.
- [ ] Show a learned concept changing the composition/forms of a place, beyond recoloring.
- [ ] Include desirable collectible items and how they appear when kept at home.

Acceptance: a clear art reference and native-size proof guide subsequent pixel
work; detail, characters and altered perception belong to the same world.

### Priority 2. Prototype one exposure-and-language encounter

Develop alongside the art direction, ahead of order-interface polish. See
DESIGN.md, “Proposed encounter: The Unfinished Word”; details are proposals.

- [ ] Re-read terminal exposure and encounter rules before implementation.
- [ ] Choose the entity's visual identity and a single meaningful language action.
- [ ] Let Bram deliberately seek the exposure needed to perceive communication.
- [ ] Teach a sign through repeated action and response, not just a text tutorial.
- [ ] Apply the learned meaning to a network choice with a resource consequence.
- [ ] Keep knowledge and physical consequences after exposure changes.
- [ ] Define losing sight during approach/conversation, retries, costs and
  cancellation; no softlocks or consumption on failed attempts.
- [ ] Playtest whether the player understands the sign and wants to use it again.

Acceptance: perception enables understanding, understanding enables agency, and
that agency matters to gathering/spending in the persistent world. One authored
encounter is enough for the experiment; no live AI or full language parser.

## Extraction, hideout and item design (new direction)

- [ ] Outline the smallest expedition -> extraction -> hideout loop, with one
  functional collectible and one useful hideout improvement.
- [ ] Define carrying, extraction, failure/loss and safe-storage rules; none are settled.
- [ ] Decide how view-specific item availability maps to persistent core identities.
- [ ] Save exact item instances, acquired knowledge and hideout changes across sessions.
- [ ] Define a bounded effect vocabulary and validation rules using authored items first.
- [ ] Explore a small multivariate fungal exposure profile; distinguish mixture
  from intensity while retaining the played dwarf as its sole owner.
- [ ] Define item affinities and persistent origin/discovery imprints; choose when
  an imprint is assigned and whether it can deliberately change later.
- [ ] Prototype two examples of the same base item with different imprints and
  clear functional/visual differences under different exposure profiles.
- [ ] Treat view/dimension identifiers as provenance, not a substitute for rules;
  retain resolved imprints and versioned behavior when saving or trading.
- [ ] Develop evocative names and motifs for fungal influences without locking
  in literal polypore/bolete classes or generic magic A/B/C labels.
- [ ] Prototype one item whose effective stats change with view and one equipment
  effect that changes perception; these may be demonstrated by the same item.
- [ ] Separate persistent item state from effective stats; choose durability/wear
  rules across view changes and make their cause legible in the item overlay.
- [ ] Specify deterministic equipment/view evaluation and stacking; prevent
  accidental oscillation, free repairs, rerolls or duplicate bonuses.
- [ ] Preserve intrinsic item state in trades while allowing the recipient's view
  to yield different effective stats.
- [ ] Research native link-cable support and item exchange feasibility; separate
  this from the later Wi-Fi/LLM path. Then scope compatibility and safe transfers.
- [ ] Keep the detailed design in DESIGN.md's expanded-direction section current.

## Supporting gameplay backlog

The following support the priority encounter as needed; they are not a sequence
of prerequisites to finish first. Order feedback remains lower priority.

### Make spore exposure change play

- [ ] Re-read the terminal exposure/perception code before choosing the ported rules.
- [ ] Prototype location-based exposure and a way to reduce it; decide whether
  consumable doses belong in this first loop.
- [ ] Build a small number of perceptual states with distinct discoveries,
  reachable interactions or characters, rather than palette changes alone.
- [ ] Decide what Reveal adds to ordinary exposure-driven perception, including
  what happens when a queued target becomes imperceptible before arrival.
- [ ] Communicate exposure through the world; keep raw values in debugging tools.

Acceptance: entering and leaving a spore-rich place changes a meaningful choice;
the consequences of completed work survive the change in perception.

### Give the mycelial network a practical purpose

- [ ] Choose ONE initial function: connected growth, resource transport, or
  spell propagation. These are alternatives to evaluate, not three commitments.
- [ ] Make connectivity affect that function, with a clear visible cause/effect.
- [ ] Let the player extend or restore one connection and see the resulting benefit.
- [ ] Tie traveling signals to actual network activity as well as atmosphere.

Acceptance: where a connection goes matters more than the number of roots lit.

### Establish a resource loop with real choices

- [ ] Review terminal gathering/building mechanics and select the smallest useful
  subset. Do not assume every terminal feature should be ported.
- [ ] Balance gathering, regrowth and spending so fungi have competing uses.
- [ ] Add one useful construction or improvement only after deciding what problem
  it solves. A bridge, growing bed or store is a candidate, not an agreed feature.
- [ ] If construction is queued, reserve its costs and define cancellation/refunds.
- [ ] Decide the forge's role: give it one useful conversion, defer it, or replace
  the landmark. The terminal Sporeforge interaction is currently a TBD stub.
- [ ] Build a short playable objective that demonstrates the loop and leaves
  room for experimentation, rather than relying only on the three-root ending.

Acceptance: the player has a reason both to gather and to save/spend resources,
with visible consequences and no resource-duplication or unpaid-work loopholes.

### Connect characters and language to that world

- [ ] Give one offline NPC a routine, a need, and a reaction to a player action.
- [ ] Prototype one learnable sign or word that enables a useful network or
  character interaction; keep its meaning consistent and discoverable in play.
- [ ] Make one encounter depend on the played dwarf's perception and world state.
- [ ] Give an encounter a persistent consequence: access, knowledge, relationship,
  or a change in the environment. Keep the implementation deterministic for MVP.
- [ ] Revisit the provisional talk rule after playtesting: earlier orders finish,
  talk is last, and no further orders are admitted until conversation ends.

Acceptance: at least one character feels situated in the simulation rather than
serving only as a stationary instruction box.

### Deferred: make orders and actions legible

- [ ] Mark pending targets on the map; distinguish the active job from waiting work.
- [ ] Show what A will do at the cursor: move, harvest, talk, or unavailable.
- [ ] Add a compact queue overview under Start, with pending-order cancellation.
- [ ] Give unobtrusive feedback for blocked ground, a full queue, insufficient
  resources, hidden targets and the pending-talk barrier. Avoid modal messages
  that stop work merely to reject an order.
- [ ] Playtest rapid taps/holds and menu transitions on the browser and Chromatic.

Acceptance: a first-time player can predict A's effect and explain what Bram is
currently doing, what comes next, and why an attempted action did not happen.

## Atmosphere pass

First pass implemented October 10. Keep iterating without obscuring orders or
interactables; more environmental detail and livelier characters remain useful.

- [x] Initial localized spore/breathing animation, water and ember motion alongside existing roots.
- [x] Initial mineral, fungal-gill and forge detail pass.
- [ ] Further improve landmark recognition and character/environment animation.
- [ ] Rich neon transformations during altered perception, with readable cursor,
  worker and job markers. Preserve quiet areas so important pixels stand out.
- [x] Author and import original looping soundtrack; routine orders stay quiet.
- [ ] Listening playtest: balance score against spell sounds and check loop feel.
- [ ] Check tile/palette/sprite budgets and actual frame rate while effects run
  alongside work, menus and movement. Validate audio separately from screenshots.

## Decisions to keep open

- [ ] Should spells be dwarf actions with travel/range, time and queued costs?
  Currently B casts immediately at the cursor. Resolve this before adding spells.
- [ ] What meaningful benefit and tradeoff should high exposure offer? Do not
  automatically turn it into a generic damage or sanity meter.
- [ ] Is the long-term experience one dwarf's strategy/RPG or a multi-worker colony?
  Keep the MVP to one played dwarf until the first loop is compelling.
- [ ] Should waiting move orders be cancellable, replaceable, or reorderable?
- [ ] Which menus pause simulation, and how is that communicated?
- [ ] What is the simplest useful actor-collision policy? Workers currently pass
  through other actors; routes assume fixed terrain.

## Before calling it a playable MVP

- [ ] Save/load and restart behavior appropriate to a cartridge session.
- [ ] A complete short session: discover, designate, gather, spend, reveal, react.
- [x] Boot menu with New Game and optional Controls pages; replace mandatory opening instructions.
- [ ] Further onboarding through play.
- [ ] Browser and physical Chromatic checks for responsiveness, readability,
  sustained frame rate and music; no claims based solely on compilation.
- [ ] Extend pathfinding when terrain becomes mutable; current paths are compiled
  from the fixed room and must be regenerated after collision changes.

## Later, outside the offline MVP

- [ ] Live generated characters/events and LLM/Jev judgments, after deciding the
  hardware/network architecture. The world/order loop must not wait on model calls.
- [ ] Multiple workers, larger maps, a broader economy and combat only if they
  strengthen the tested core rather than adding disconnected systems.

## Implemented and exercised

- [x] Native GBC room with color palettes and a controllable cursor.
- [x] Faster cursor input; A queues FIFO movement, harvesting and a final talk order.
- [x] Autonomous dwarf movement, work completion, resource yield and pending
  harvest cancellation; bounded 16-order queue.
- [x] Reveal Mycelium, animated signals, independent root awakening and paid regrowth.
- [x] Played-dwarf exposure from harvesting affects Reveal duration/repetition.
- [x] Separate Start inventory/status and Select spell overlays.
- [x] A equips in place with visible feedback; B closes without equipping a
  merely highlighted spell. Repetitive order/harvest beeps removed.

See DESIGN.md for current rules and limitations, and PLAYTEST.md for evidence.

Latest polish: removed remaining spell beeps, added moving bass phrases, and
animated the third forge flame. Native boot/menu, Reveal and audio comparison
checks passed; subjective audio balance remains a listening task.

## Trade identity and turn-based combat

- [ ] Keep intrinsic item stats/affinities fixed across trade; expose situational
  modifiers separately. No recipient-side reroll or reinterpretation of base stats.
- [ ] Start with a few clear metrics and authored tradeoffs; test for dominated
  junk items before expanding generation or the affinity vocabulary.
- [ ] Explore Pokemon's collectible identity, affinity and trading lessons without
  assuming creature capture or its full combat structure.
- [ ] Prototype the agreed hybrid: real-time expeditions with turn-based fights
  that pause world simulation. Start with one opponent, a few actions and two loadouts.
- [ ] Freeze queued work, movement and environmental progression during fights;
  resume afterward without elapsed-time catch-up. Battle effects advance by battle rules.
- [ ] Define engagement, escape and loss before expanding combat content.

## Trade recommendations: resonance and usefulness

Agreed design direction; future trading work, below the current concept-art and
encounter priorities. See DESIGN.md, “Trade discovery.” No ranking is implemented.

- [ ] Define resonance from item affinities and the recipient dwarf's exposure
  spectrum using actual gameplay interactions.
- [ ] Define contextual usefulness from equipment, missing capabilities and
  selected expedition/homebase conditions; distinguish it from similarity.
- [ ] Prototype “12 offers / up to 3 promising matches,” with concise reasons,
  intrinsic-stat inspection and a browse-all option on the native screen.
- [ ] Explore resonance, weakness coverage and expedition-fit suggestions without
  forcing three recommendations or a single opaque player-facing score.
- [ ] Derive explanations from implemented rules, including material conditions
  and drawbacks; do not invent benefits or infer an unselected destination.
- [ ] Test close matches, useful off-affinity items, redundant equipment and
  inventories with no good match. Recompute for changed player context.
- [ ] Keep recommendations separate from trade confirmation; preserve each item's
  intrinsic qualities regardless of ranking or recipient.

Acceptance: a player can explain why an offer might help in one short sentence,
inspect the tradeoff and choose any available offer. Ranking weights remain open
until functional item and affinity rules support meaningful comparisons.

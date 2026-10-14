# The Pale Cap — living TODO

Updated October 11, 2026. This is the GBC adaptation's backlog; the terminal
repository keeps its own TODO. The order below is a recommendation, not a set
of settled design decisions. Keep experiments small and playable, update this
file after each pass, and record verified behavior in PLAYTEST.md.

## Checkpoint before rendering overhaul — October 11

- [x] Preserve integrated home/extraction/save work and the separate Hi-Color study
  in a checkpoint PR. The concept portfolio remains local and ignored.
- [x] Refresh READMEs and preserve GB Studio, GBVM, Binjgb and Hi-Color notices;
  see `../THIRD_PARTY_NOTICES.md`.
- [ ] Confirm the GBDK example license explicitly covers Toxa's Hi-Color ISR
  before promoting the copied renderer into a release.
- [ ] Select a project-wide license for original code and art; the existing
  GB Studio MIT notice is an attribution, not a blanket licensing decision.
- [x] Integrate the 104px Hi-Color Hearth with functional home menus and validate
  short input taps, stable consecutive frames, music cadence/output, item
  transfers, extraction, cold boot and soft reset in the native emulator.
- [x] Flash integrated Hi-Color to the user's Chromatic; user reports the Hearth
  room looks excellent on the physical screen.
- [x] Fix the old-art flash on entry and palette/tile snow during transitions;
  verify consecutive frames and music timing in the emulator.
- [x] Remove the obsolete Hearth illustration from the built ROM. Preserve its
  source file; use one blank backing tile for the engine's native scene.
- [x] Reflash the transition fix and confirm clean entry/exit on the Chromatic;
  user reports it looks good. Other hardware checks below remain separate.
- [ ] Check the menu boundary, music quality, response and physical save retention
  individually on hardware. Sprite highlights are still deferred.

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

## Current priorities (user direction, October 11)

Next major milestone: overhaul expedition visuals and gameplay. The physical
Hearth test establishes the desired visual quality; the current overworld is a
prototype, not the art direction to preserve. Start with one cohesive, playable
biome slice before expanding the world. See DESIGN.md's overworld milestone.

- [x] Build a separate six-view hardware comparison ROM from the three existing
  studies; emulator-check controls and stable rendering. See
  `art-tests/overworld-gallery/README.md`. Source concepts stay local and ignored.
- [x] Compare all three directions and both exposure views on the Chromatic;
  user reports they look great, while noting unintended differences across states.
- [x] Build isolated interactive Hi-Color Heartwood: moving Bram, cursor/FIFO,
  obstacle routing, one harvested patch, independent reveal and persistent state.
  Emulator checks pass; see `art-tests/heartwood-playable/README.md`.
- [ ] Review the interactive Hi-Color scene on hardware, including sprite fit,
  subtle reveal readability, partial patch transitions and movement feel.
- [ ] Budget music, more actors and production scheduling with the Hi-Color ISR
  before integrating this experiment into the main game.
- [ ] Review the designer's modular production candidates: exact tiles/sprites,
  harvested/regrowth states, and storyboards assembled from those same assets.

- [ ] Prepare a native-size expedition composition with Bram, a landmark,
  harvestable fungal growth, a mycelial route and a readable extraction point.
- [ ] Compare ordinary and elevated-exposure views of that same composition;
  preserve geography and show a meaningful discovery beyond recoloring.
- [ ] Review candidate tile/character replacements individually before adopting
  them; keep approved Hearth and item artwork and all source concepts intact.
- [ ] Integrate a small slice with a useful fork interaction, resource tradeoff
  and return-to-stash payoff; audit existing terminal mechanics before redesign.
- [ ] Validate moving actors, cursor response, queued work, music and rendering
  budgets together. Do not assume the static Hearth renderer suits the overworld.

The earlier illustrated Bag -> Inspect, dark/cyan menus, hideout-only saving and
direct-to-home boot milestone is implemented. Home improvement and a useful fork
effect remain unfinished. The extraction foundation already exists.
See [EXPEDITION-SLICE.md](EXPEDITION-SLICE.md) for a concrete proposal and acceptance
checks. Numeric limits, loss rules and the fork effect are provisional test choices.
The earlier encounter work remains valuable but is no longer the immediate first
implementation task. Preserve existing assets; review replacements individually.

- [x] Draft carrying, return, storage, save boundaries and one improvement proposal.
- [x] Prove one detailed item inspection image in a separate native GBC ROM.
- [ ] Restore richer frame ornament and explore brighter native palettes separately.
- [ ] Explore three illustrated hideout concepts with functional hotspot composition.
- [ ] Implement stable item ownership and safe persistence before adding variants.
- [ ] Implement one pickup -> use -> return -> deposit -> reload loop.
- [ ] Test one home improvement and resource tradeoff.
- [ ] Resolve fork pulse overlap with Reveal through play, not additional terminology.
- [ ] Keep a shared fork-family overworld icon as sufficient for the first slice;
  leave visible equipped items undecided.

## Continuing art and encounter work

### Establish visual direction with concept art and native assets

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

### Prototype one exposure-and-language encounter

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

- [x] Outline the smallest expedition -> extraction -> hideout loop, with one
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

## October 11 implementation checkpoint

- [x] Session-only native pickup -> equip -> queued return -> stash -> withdrawal.
- [x] Separate locked bag/home overlays and resource deposit/withdrawal.
- [x] Transfer conservation/equip-ownership checks against native implementation.
- [x] Implement home-only semantic saves; omit mid-run resume and queue serialization.
- [x] Valid save boots straight into hideout; no save retains startup/New Game.
- [x] Reject incompatible/corrupt saves clearly and preserve recoverable data.
- [x] Connect approved Vermilion artwork to Bag -> Inspect.
- [x] Replace pale menu treatment with dark/cyan styling; verify native readability.
- [x] Replace temporary home overlay with a reviewed illustrated home scene.
- [x] Remove player-facing coordinates and remote Collect fork shortcut in v2.
- [x] Grant the first fork through Luma's queued conversation; native gift dialogue checked.
- [ ] Future ground pickups need visible reviewed icons and the same ownership path.
- [ ] Add general item slots/capacity; current implementation proves one instance only.
- [ ] Add extraction confirmation and one home improvement, then fork effect.
- [ ] Resolve old preview recording-close acknowledgement before switching player.

See PLAYTEST.md for exact build, checks and remaining limitations.

## Home integration v1 completed

- [x] Root Hearth concept adapted into a native illustrated home scene.
- [x] Vermilion inspection reachable from Bag and Stash; source art preserved.
- [x] Dark/cyan/cream shared menu and dialogue palette.
- [x] Home-only explicit saving of semantic state, without queued work.
- [x] Valid save boots directly home; no save shows startup choices.
- [x] Version/checksum/commit validation with a recoverable previous record.
- [x] Native cold boot from battery data retains the stored fork.
- [ ] Verify browser persistence independently and physical cartridge retention.
- [ ] Improve hotspot placement/selection visuals after reviewing the home scene.
- [ ] Implement one useful home improvement and the fork's distinct active effect.
- [ ] Decide departure-loss bookkeeping and home autosave policy; neither is implicit.

See the remaining unchecked tasks above for broader systems;
PLAYTEST.md distinguishes native checks from outstanding browser/hardware checks.

### Gillsong inspection flow — October 11

Integrated the Vermilion study’s cyan ornament pulse into item inspection. It starts automatically; B returns as before. The fork, text, and other palettes remain static. Native emulator checked all 192 frames: exactly 245 ornament pixels animate, followed by the original rest interval. Save/load and both inspection return paths pass. Browser export rebuilt; refresh the preview to load it. Hardware animation remains untested.

### Native art pipeline — October 11

- [x] Diagnose tile-by-tile palette discontinuities in Root Hearth.
- [x] Produce a separate coherent conversion candidate with repeatable RGB555,
  continuity-aware palette assignment, frozen-palette support and encoded-data audit.
- [ ] Review Root Hearth candidate before replacing the individual game asset.
- [ ] Author clean native pixel clusters and separated interactive room objects.
- [x] Add explicit material-region constraints and reviewed palette locks to the
  converter, plus a tile-edge contrast diagnostic and a repo-local workflow skill.
- [ ] Author the chest light pool's native pixel transitions and review partial
  floor-region boundary tiles before replacing the background.
- [ ] Verify approved replacement in a cartridge build, with menus and on hardware.

See ART-PIPELINE.md and art-tests/root-hearth-conversion/README.md.

### Generative scene packages — October 14

- [x] Test Jev 1.14 on scene images with full-image context and explicit crops;
  retain terrain and proposed interaction categories independently.
- [x] Run a full pass on decoded native Hi-Color Heartwood pixels, preserving
  the original scene and all saved classifications.
- [x] Compile a candidate scene package with frozen interpretation, bounded
  harvest sites, reachable approach cells, stable IDs and art-state job requests.
- [x] Test deterministic compilation and one-yield state transitions through
  serialization. This is an offline package test, not a playable generated ROM.
- [x] Add a vision-model proposal → Jev → browser Inspect experiment on decoded
  Heartwood pixels, retaining proposed names, prose, labels and rejected candidates.
- [x] Add independent walkable/fungus/harvest-candidate/water/structure labels;
  preserve overlap without inferring harvesting solely from fungal identity.
- [ ] Review Inspect copy, target bounds and overlapping labels; compare disagreements
  with the older terrain/interaction pass, especially boardwalk access and heights.
- [ ] Integrate reviewed objects/labels with the movement and interaction package;
  keep evidence separate from explicit gameplay rules and persistent object states.
- [ ] Review provisional object regions/sites; refine beyond coarse 16x16 cells.
- [ ] Add actor clearance, elevations, foreground overlap and explicit entrances/
  exits; validate extraction reachability before accepting a playable package.
- [ ] Add before/after Jev checks for intended changes, retained objects, lighting
  and sprite readability alongside exact unchanged-pixel and hardware audits.
- [ ] Generate the requested local art-state variants from the exact native master;
  verify unchanged exterior pixels, frozen palette use and tile/upload budgets.
- [ ] Compile one package into a standalone playable cartridge, verify queue/work/
  reward/revisit behavior, then test on Chromatic before production integration.
- [ ] Add bounded templates beyond harvest and tune yields/costs against the
  extraction economy. Jev authors proposals; supported code implements effects.
- [ ] Extend the frozen package format to alternate exposure/language views and
  later remote delivery while preserving object state and traded-item identity.

See SCENE-GENERATION.md and art-tests/jev-scene-probe/README.md.

- [ ] Compare an authored standard Hearth background, a sprite-augmented version,
  and an isolated scanline-palette/Hi-Color rendering study using the same source.
- [ ] For Hi-Color, verify menu/text stability, LCD interrupt coexistence, scene
  exit restoration, music/input timing, and physical Chromatic output before integration.

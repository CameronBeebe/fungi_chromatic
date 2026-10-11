# The Pale Cap: offline prototype

## Agreed direction

A psychedelic real-time strategy looter extraction game, with a buildable hideout,
tradable items, cursor-based orders and an autonomous played dwarf.
This is the intended identity; the current prototype implements only a small slice.
The cursor is an interface, not a separate character. The played dwarf's spore
exposure determines the player's view. There is no separate player exposure and
no colony-wide exposure pool. Other characters may have different awareness.

One physical world persists through perceptual changes: resources, designations,
work, and connected roots do not reset when sight fades. Spore exposure is a
character property; its raw value stays out of ordinary player-facing UI.

The MVP is deterministic and offline. LLM generation and Jev judgments belong
to a later expansion, subject to the proposed Wi-Fi hardware/firmware work. No
network or model dependency belongs in the order-processing loop. Prepared
content can be authored or generated ahead of time and compiled into the ROM.

## Design framework

The inspirations are a vocabulary for an original game, not a requirement to
reproduce their settings or add every associated mechanic.

- **Dune / spice:** a desirable commodity connects gathering, spending, access
  and power. Spores affect cognition, perception and abilities as well as the
  economy. High exposure should offer reasons to seek it; it is not automatically
  a poison or sanity meter. Concrete benefits and tradeoffs still need playtests.
- **McKenna / language / strange intelligences:** language is a core interaction
  medium. Words, names, patterned signals and acts of interpretation should
  eventually change what the dwarf can understand or do. Machine-elf-like
  encounters suggest unfamiliar communicative beings, not just visual noise.
- **Psychonauts / perceptual environments:** altered awareness can change the
  experienced character of a place and its available encounters. One persistent
  world supports these views; ordinary perception is not the privileged truth.
- **Real-time strategy / dwarf simulation:** designation, autonomous execution,
  gathering and competing resource uses give discoveries practical consequences.
  The cursor directs Bram; his exposure determines the player's perception.

A proposed unifying loop is: gather a desirable resource, choose how to spend or
use it, perceive a previously inaccessible signal or being, understand something,
and apply that knowledge to the same world. This is a design target, not a claim
that the current three-root prototype implements the whole loop.

Language must become more than decorative glyphs. A small offline experiment
could teach one repeatable sign through an encounter, then let recognizing or
using it change one network interaction. Exact grammar, bargaining, naming and
spell composition remain open; do not commit to all of them at once. Authored,
deterministic content can prove this without live LLM/Jev calls.

Atmosphere should imply a living, communicative ecology: recurring motifs,
responses, pulses, quiet spaces and luminous detail. Keep the cursor, dwarf and
useful targets readable through changes in perception. Do not equate maximum
full-screen flicker with psychedelic depth.

## Implemented slice

Bram is the single played dwarf. The cursor can cross walls and water to mark
fungi. Bram follows a bounded FIFO queue (up to 16 orders), walks a precomputed shortest
terrain route, works for 90 frames, and only
then adds a fungus to inventory. Pending orders can be cancelled; a job already
being worked cannot. The eight patches have independent pending/working/done
states, so repeated inputs do not grant duplicate resources.

For this playtest, A on empty walkable ground adds a movement order; A on a
visible character appends a conversation. That conversation closes admission
until Bram finishes the prior orders, approaches the character and finishes
talking. Further A orders are ignored without pausing work. This is an
experiment, not a settled interaction design. Movement, harvest orders and spell casts are silent; the score supplies MVP audio.

Cursor input uses immediate press handling and a per-frame native poll, with
an eight-engine-frame initial repeat delay and four-frame repeat interval.
The cursor remains free to cross terrain. A local Colony Controls plugin owns
the FIFO and cursor timing; editable native events own rewards and dialogue.

Fungal Bloom costs two fungi to awaken a root, in any order. Once awake, a root
can regrow its harvested patches for one fungus. Unaffordable casts do nothing.
Regrowth leaves pending and active harvests alone. The grove, forge and crown
are small authored content examples, not intended as the final progression model.

Harvesting exposes Bram to spores: the prototype starts at 50 and adds five per
completed harvest, up to 100. This same value determines Reveal duration and
signal repetitions. Reveal lights a connected mycelial overlay, animates root
rings, changes the grotto's palette, and sends three-cell signals from the crown.
The temporary sight timer is an effect duration, not a second exposure value.

Vesper is currently a scripted encounter after three roots awaken, visible while
Reveal is active. Per-NPC exposure and threshold-driven encounters are not yet
implemented. The old two-ending dialogue remains as placeholder RPG content.

## Deliberately provisional

Spells currently execute immediately at the cursor. Queued dwarf casting,
travel/range requirements, casting time, and interruptibility need a play-design
decision; they are not implemented by the harvest queue. Reveal currently costs
nothing. Bloom uses fungi rather than the terminal game's mana costs.

Exposure currently comes from harvesting; proximity accumulation, decay, consumable
doses, and distinct perception bands are not implemented. Do not describe the
prototype's recoloring as a complete model of those systems.

The intended RPG layer is character-specific perception, relationships, discoveries,
and persistent consequences. Conventional RTS combat is not necessary to prove
this loop. Multi-dwarf control and selection-dependent perception remain open.

## Source references

The sibling terminal repository supplies the design basis:
`fungi_fortress/magic.py` (Reveal, Bloom, network signals), `task_manager.py`,
`dwarf_mind.py`, `game_logic.py` (designation, path selection, work completion),
`spice.py` (exposure), plus `PLANNING.md` and `TODO.md`.

This is a small native adaptation, not the full Python simulation. Routes are
compiled for every walkable origin/destination in the fixed collision map; run
`tools/build_navigation.py` after terrain changes.
Worker routes ignore character collisions, allowing Bram to pass through other
actors. Menus/dialogue can pause work. Saves, audio polish, dynamic terrain,
multiple workers, and physical Chromatic validation are outside this build.

## Menu and atmosphere iteration

Select opens a full-screen spell panel with an explicit equipped label, two
choices and costs. The initial highlight follows the equipped spell. A equips
and redraws the equipped label while keeping the menu open. B closes without
equipping a merely highlighted choice; spells already equipped with A persist. Start opens inventory/status. These
use the native window overlay, not dialogue pages. Both pause play while open.

For MVP audio, favor a restrained looping score with quiet routine actions.
The first atmosphere pass adds an original looping score, A Grammar of Spores,
with call-and-response phrases and a soft bass part. Routine orders remain quiet.
The room now has mineral seams, fungal gills, forge details, animated water,
embers, localized spore/breathing cells, and three changing glyph cells during
Reveal. These glyphs are visual motifs, not yet a decipherable language system.
The new background preserves terrain and palette assignments; animation replaces
native tiles. Audio balance still needs a listening playtest. The bass now uses eight notes per
phrase, and all three forge flames animate with offset phases.

Boot opens a New Game / Controls overlay before order handlers are installed.
Controls has two optional pages and returns to the title; New Game enters the
room directly. The former mandatory instruction dialogue is replaced by this
menu. No Continue option is offered until saving exists.

The forge remains a landmark near a root in this prototype. The terminal game's
`interact_dwarven_sporeforge_logic` is a TBD stub, despite lore about crafting
spore-enchanted gear. A concrete forge economy has not been ported or invented.

## Proposed encounter: The Unfinished Word

Design sketch for discussion, not an approved implementation specification.
Concept art and this encounter take priority over additional order UI polish.

**Place and being.** A split mycelial junction surrounds a small, apparently
inert assemblage. At sufficient exposure, Bram perceives it as a busy intelligence
folding signs out of its own body. Candidate visual direction: articulated seed
shells, mineral facets and fungal filaments, with gestures that briefly form
readable negative space. Its identity should emerge from concept exploration;
“machine elf” is an inspiration, not a settled humanoid sprite design.

**Desire and approach.** A visibly rich growth beyond the junction gives Bram a
reason to investigate. A nearby spore-rich pocket lets him seek exposure on
purpose. This requires a deliberate exposure rule; exact thresholds, accumulation
and reduction are still open. Cursor position never grants exposure. Reveal may
clarify the connecting threads while exposure makes the being's communication
perceptible; those roles must be distinguished in the prototype.

**Language as action.** Working gloss: “JOIN.” The being brings separated forms
together; the resulting sign travels into two filaments, which briefly connect.
Repeat the same gesture, sign and consequence so the player can infer a meaning.
A short authored exchange can invite a response without translating everything.
Learning records a usable sign, not a requirement to memorize a timed sequence.
The being is demonstrating a way to act on the world, not handing over a password.

**Strategic use.** One candidate experiment lets Bram apply JOIN to either of
two prepared network branches: connect a productive fungal bed or connect a
spore-rich growth useful for returning to altered perception. Feeding the chosen
connection spends gathered fungi. Start with one affordable connection; allow
later gathering to fund the other so the first choice is not an irreversible
trap. Exact yield, costs and behavior are unbalanced proposals. Implement only
one small network benefit per branch, not transport, combat and a new crafting
system at once.

**Persistence and recovery.** Learned knowledge and established connections
survive reduced exposure. The entity can become imperceptible without erasing
the encounter. Preserve encounter progress on losing sight; failed attempts do
not spend resources. Decide whether initiation requires visibility but an active
conversation completes, before implementing its queue behavior. Knowledge may
remain usable at lower exposure; whether execution needs altered perception is
an open choice, not a second player exposure meter.

**Art deliverables.** Explore the junction in two perceptual states, the entity
in resting/communicating poses, Bram's silhouette and equipment, and the JOIN
motif echoed in both gesture and network behavior. Then test a native-size room
composition, sprite silhouettes and a few communication cels. Carry the best
visual direction into implementation rather than adding unrelated detail to the
current placeholder assets.

**Scope and success.** One room, one being, one learned meaning, two applications,
a deterministic authored exchange and persistent consequences. No free-text
input or generative model is needed. Success means the player can explain what
the sign does, choose a useful application, and recognize it elsewhere. Avoid a
mandatory rhythm puzzle, arbitrary symbol matching or a long explanatory lecture.

## Expanded direction: expeditions, hideout and exchange

User direction, October 10: psychedelic real-time strategy looter extraction.
Build a hideout; seek discoveries across biomes and perceptual views; bring items
back, preserve them, use them, and trade them. Link-cable item exchange is part of
the intended direction. No link protocol, hardware compatibility, multiplayer,
save system or extraction rules have yet been implemented or verified. Live
LLM/Jev and proposed Wi-Fi work remain outside the offline MVP; link trading is
a separate feature and should not be conflated with that network dependency.

### Fungal ecology and visual value

Hyphae, mycelium, sclerotia, spores and flushes belong in the design vocabulary,
with distinct appearances and useful roles. Proposed game abstractions include
hyphal connections, sclerotial reserves, dispersible/collectible spores and timed
flushes of harvestable growth. These are candidates, not a claim of biological
simulation or settled rules. Biomes should differ in silhouettes, substrates,
growth rhythms, resources and perceptual transformations as well as palettes.

Beauty on the Chromatic screen has intrinsic value. Concept art, compelling
sprites, animation and distinctive places are core product work, not merely
polish deferred until all systems are built. Tie attractive discoveries to
solid gathering, spending and item behavior without requiring every beautiful
detail to justify itself mechanically.

### Language changes the experienced world

Language can change how the world LOOKS and how its objects are organized into
meaningful categories. The user's reference is Kantian categories through a
psychedelic lens: an artistic design inspiration, not a strict philosophical
model. Learning a concept might make a mass of threads appear as discrete
vessels, pathways or beings, with different recognizable opportunities.

A view may expose unique items or a different distribution of opportunities in
the same persistent core. Define stable underlying identities and view-dependent
availability so changing views cannot repeatedly duplicate an already collected
object. Decide which effects are perceptual reorganization, newly accessible
entities, or actual changes to the world. Knowledge, exposure and item effects
can all influence the view; exposure itself always belongs to the played dwarf.
The JOIN encounter is only one candidate and must not constrain language to
verbs that operate otherwise unchanged scenery.

### Expedition loop and hideout

Proposed loop: prepare at the hideout, venture into a biome, shape perception,
find and gather useful discoveries while directing real-time work, choose what
to carry back, extract, then preserve, cultivate, build, equip or trade.

The hideout is a persistent place the player builds and personalizes. Candidate
functions are storage, cultivation, specimen display, preparation and a record
of learned language. Its appearance and available uses may themselves change
with learned concepts or perception. Select a small useful subset for the first
slice rather than immediately implementing every station.

“Saving a discovery” is both a gameplay idea (bringing it home or stabilizing it)
and a persistence requirement (retaining the exact item across sessions). These
must have explicit rules. Expedition loss, extraction conditions, carrying
limits, safe storage and whether some finds require stabilization remain open;
combat, permanent loss and a timer are not implied commitments.

### Functional items, generation and link trading

Items should have actual, distinctive behavior. Future generation can compose
within a rich but bounded, versioned vocabulary of effects, conditions, targets,
costs and limits. Schema-valid data alone does not guarantee a useful or balanced
item: the game must implement those effects and validate combinations and budgets.
Proposed data also includes persistent instance identity, origin/seed, visual
representation and discovery conditions. Preserve resolved item properties,
not just prose or a seed that might change meaning after a generator update.

Trade items over a link cable as a desired future interaction between players.
A receiving game must understand and retain the item's functional definition;
its behavior cannot depend on the originating player's model service. Research
actual platform support before promising implementation. Plan compatibility,
mutual confirmation, capacity checks, interrupted-transfer recovery and save
integrity. These are future implementation requirements, not an implemented
protocol or a reason to require online services.

An offline authored item can prove the same discovery/use/extraction/storage
loop now. Later generation should expand a working design vocabulary. Variety
and replay value are goals; reliable endless novelty is not established merely
by adding a model or a large schema.

### Items and views influence each other

User clarification: a view can change an item's effective power, durability or
other stats, as well as its appearance. Equipping an item can itself change the
look of the game or the view through which the core is experienced. These are
intended capabilities; exact formulas and interactions are not yet settled.

Proposed foundation: persist an item's identity, intrinsic properties and mutable
state; derive its currently effective properties from the active view, equipment,
learned concepts and relevant world conditions. Distinguish changed interpretation
from permanent mutation. A view change must not silently reroll an item, duplicate
it, or repair wear unless an explicit mechanic grants that effect.

Durability needs a deliberate rule. One candidate stores accumulated wear and
lets the view change resistance to new wear; a more ambitious option also changes
effective capacity, with an explicit policy for an item becoming unusable in one
view and usable in another. Avoid implementing this as a free refill on switching.
Neither policy is chosen yet. Show effective stats and why they differ in item UI.

Define a deterministic evaluation order for equipment that alters a view and
views that alter equipment. Prevent accidental feedback oscillation or repeated
bonus stacking. Trading preserves intrinsic properties and mutable state; the
recipient's view may produce different effective stats. Make this understandable
without requiring identical perception between players.

Illustrative item, not a committed feature: a sclerotial lens reveals resource
patterns when equipped; in a compatible perceptual state it improves an existing
harvest ability, while use wears it according to explicit rules. Its visual and
functional effects use the same implemented vocabulary as other items.

The quality and expressive range of the underlying mechanics determine how well
items and eventual generation scale. Develop a few satisfying effects, clear
interactions and meaningful costs first; expand composition as those rules become
robust. Large numbers of stat combinations alone are not evidence of depth.

### Exposure spectra and item imprints

User direction: exposure may become a multivariate profile of fungal influences,
not just one low-to-high intensity. Polypore/ bolete affinities and fictional
fungal A/B/C influences are illustrative labels, not settled taxonomy, magical
schools or biological claims. Find evocative names and visual identities through
art and writing. The profile still belongs to the played dwarf; no separate
player/cursor exposure is introduced. The current implementation remains scalar.

Distinguish three proposed concepts:

- Bram's changing exposure profile: the mixture of influences shaping perception.
- A view's conditions: a reproducible configuration of the persistent core's
  perceptual and gameplay rules, potentially including which effects are stronger.
- An item's persistent imprint: characteristics recorded from its origin or the
  conditions under which it was discovered, formed or extracted. Choose the exact
  imprint moment deliberately; these are alternatives, not equivalent events.

An item's affinities need not be identical to Bram's current profile. Its imprint
persists after the trip, while present conditions may resonate with, suppress or
transform its effective behavior. Whether affinities can later be changed by
cultivation, crafting or deliberate re-imprinting is an open design question.
“Alignment” here denotes affinity/character, not necessarily morality or a
binary faction choice.

Illustrative example: two daggers share a base function but originate in distinct
view configurations. One retains an imprint favoring effect C; another favors a
different effect. Their effective strengths depend on implemented interactions
between intrinsic imprint, current view and wielder. A numeric “dimension” ID can
identify provenance or a reproducible seed, but does not alone define behavior
or require a separate simulated world for every ID. Persist the resolved imprint
and rules version, not only a seed whose interpretation could later change.

Choose whether finding an existing object reveals a fixed imprint or actually
imprints it through discovery; avoid silently mixing the two ontologies. Preserve
core object identity and collection state across views. Exploration may change
what can be found and what qualities a find acquires, without yielding unlimited
copies of the same core object through repeated perception changes.

Begin with a small number of distinguishable influences and authored interactions.
Do not commit to one numerical axis per real fungal taxon, a huge matrix of
resistances, or thousands of meaningful dimensions before their differences are
fun and visually legible. Express profiles through motifs, colors, behavior and
language as well as optional item details; names and presentation remain open.

### Stable trade identity, legible balance, and turn-based combat

User clarification: intrinsic item characteristics remain constant across trade.
A dagger from view/dimension 1047899 with strong C affinity keeps that affinity
and its intrinsic strength in the recipient's game. Its usefulness may depend
on the expedition or homebase spectrum, but receiving it must not reroll or
rewrite those qualities. Separate explicit situational modifiers from the item
itself. Prior discussion of different effective stats should be read within this
constraint, not as a license to change a traded item's identity.

Pokemon is an explicit design influence for recognizable affinities, collectible
identity, complementary strengths and reasons to trade. This does not commit the
game to creature capture, six-member parties, or Pokemon's combat rules.

Balance priority: few well-defined, consequential metrics before a large schema.
Each affinity needs an understandable use and each stat must affect a meaningful
choice. Avoid generating a sea of dominated items through many opaque modifiers.
Use authored examples to establish tradeoffs and demand; future generation must
respect budgets and interaction rules. Recycling or salvage is a possible later
response to unwanted loot, not a substitute for worthwhile item design.

Chosen direction: real-time cursor orders, gathering and expeditions transition
into turn-based fights that pause the world. Expedition simulation, including
queued work, movement and environmental progression, stops during combat and
resumes afterward without catching up elapsed real time. Battle animations and
turn-based effects can still advance within the encounter. This lets players
consider moves without offscreen work or threats creating time pressure.
Encounter entry, retreat, loss and exact battle rules remain open. This records
the agreed design direction; combat is not implemented yet.

Prototype one opponent, a small action set and two meaningfully different item
loadouts before building a broad combat system. A readable enemy intention and
an affinity interaction could test whether preparation and perception produce
interesting choices. Keep exposure changes deliberate rather than requiring
constant menu swapping. No combat, battle UI or combat balance exists yet.

### Trade discovery: resonance and contextual usefulness

Agreed direction: help players find promising items within a trading partner's
inventory. Rich item characteristics can remain manageable if the interface
surfaces understandable synergies. An item keeps its intrinsic qualities; its
relevance is personal to the prospective recipient.

Distinguish two assessments:

- **Resonance:** compatibility between the item's affinities and the played
  dwarf's exposure spectrum. Similarity is a candidate input, not a complete
  definition of value; the actual affinity rules determine useful matches.
- **Usefulness:** what the item adds given current equipment, missing capabilities,
  the intended expedition/biome and, where relevant, the homebase spectrum.
  An off-affinity item may cover a weakness better than another close match.

Proposed trade presentation: “Player 2 has 12 items available; here are three
promising matches.” Count available offers separately from recommendations; do
not imply every offered item is useful. Show a compact shortlist, one concise
reason per item, and an option to browse everything. On the GBC screen, use
short labels and a detail page rather than assuming all explanatory copy fits
in one view. Inspect the intrinsic stats and situational effects before trading;
recommendations never select or confirm an exchange automatically.

Illustrative copy, using hypothetical items and capabilities:

- **Glassroot Dagger — Strong resonance.** Matches two dominant influences.
- **Ash Sclerotium — Covers a weakness.** Adds protection current equipment lacks.
- **Veil Lantern — Expedition match.** Helps reveal resources in the chosen biome.

These are examples, not implemented items or guaranteed benefits. Reasons must
come from the same functional rules that govern play, not invented model prose.
A recommendation can expose a drawback or condition as well as a benefit. If no
destination is selected, do not pretend to know expedition suitability.

Ranking can use internal scores, but avoid presenting one opaque percentage as
universal item quality. Prefer visible reasons and comparisons. Explore distinct
shortlist roles (resonance, coverage, expedition fit) so three similar items do
not automatically crowd out a useful alternative. Exact scoring, weighting,
normalization and thresholds remain undecided until the underlying mechanics
are defined. Re-evaluate when the relevant profile or equipment changes without
altering any item's intrinsic data.

Design test: can we explain why an item is worth considering in one short
sentence? If not, inspect whether the mechanic is unclear before adding more
metrics. Test authored inventories where a close match helps, an off-affinity
item fills a gap, a duplicate adds little, and no offer is useful. Do not force
three positive recommendations when fewer qualify. This is future trading UI;
it is not a prerequisite for the current art and encounter priorities and does
not require a live LLM/Jev service.

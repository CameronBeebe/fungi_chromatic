# Generative scene pipeline

Direction agreed October 14, 2026: generate a place whose appearance, mechanics
and changes form one coherent package. Jev may author the interpretation rather
than attempt to recover a hidden designer's answer. A strange growth may become
a harvestable resource because that is the interpretation chosen for this world.

The test of an interpretation is coherence and playability. Its classification
does not need to match an imagined canonical object label. Confidence remains
useful evidence for tuning; it is not a requirement that every creative decision
clear an accuracy threshold. Code still enforces reachable interactions, bounded
effects, item budgets, persistent identity and hardware constraints.

## Production direction

Confirmed October 14: develop this unified package workflow for production level
design. Movement/access and interaction authoring are complementary layers of the
same level, not competing prototypes. The probe explores visual decisions; the
package compiler makes those decisions persistent and mechanically constrained.
Production adoption is the direction, not a claim that the current browser study
is ready to ship on cartridge.

## Intended sequence

1. **Generation brief.** Art direction, character references, biome, exposure
   spectrum, vocabulary, supported interactions, entry/exit requirements and
   renderer budgets give the generator a bounded task. Keep images, parameters,
   seeds and model/prompt versions for provenance.
2. **Image to native art.** Develop the composition into native-resolution pixel
   art. Compile Hi-Color tiles, attributes and palette schedules under the chosen
   scene renderer. Independently decode those bytes and inspect the result.
   Concept art is not the image on which final scene mechanics are judged.
3. **Visual proposals and Jev interpretation.** A separate vision-language model
   first proposes distinctive visible objects, descriptive labels and short Inspect
   prose from the decoded native image. This is an open vocabulary proposal step;
   supported engine verbs remain a separate bounded vocabulary. Jev checks the
   proposals against pixels, including presence, visual fit, and whether Inspect
   text promises behavior the game cannot perform. Retain rejected proposals too.
   Supply the decoded native pixel image plus local crops
   from that same image. Classify terrain, proposed interactions, materials and
   relevant perceptual characteristics as separate questions. Full context and
   crops can coexist in one call. Batch large crop sets to keep requests bounded.
   API upscaling uses nearest-neighbor blocks, never smoothing or invented detail.
4. **Regions, instances and interaction sites.** A region labeled harvestable is
   not automatically a single mushroom. Resolve object extent, identity, work
   sites, foreground overlap and height. A large colony can offer small local
   harvest sites instead of disappearing in one action. Preserve those identities
   once the interpretation is accepted.
5. **Mechanical compilation.** Map decisions into supported action templates.
   Derive collision candidates and approach positions, then verify connectivity,
   actor clearance, entry/exit routes and resource rules. Keep inaccessible or
   unsupported proposals recorded; do not silently fabricate a route or ability.
   The engine determines finite costs, timing, rewards and supported effects.
6. **Local art-state jobs.** Each action specifies its physical state change:
   intact/depleted, closed/open, ordinary/revealed, and so on. Generate or author
   those variants from the exact master with explicit editable footprints.
   Unchanged pixels must remain identical. Keep palette schedules stable where
   required; a request for a patch is not evidence that a legal patch exists.
7. **Reconcile and validate.** Check the changed art against intended mechanics,
   preserve non-target objects, and revalidate navigation if the action changes
   collision. Compile pattern patches or sprites. Measure ROM/VRAM, objects per
   scanline, palette ownership, upload timing, queue responsiveness and transitions.
8. **Freeze, package, play.** Save the scene revision, object definitions, initial
   states, assets and provenance. Build a cartridge and test actual interactions
   in the native emulator and on hardware. Future delivery over Wi-Fi can use
   this same versioned package contract; it does not require network calls in
   the real-time action loop.

This is an iterative pipeline: an unworkable interpretation may require a new
scene layout or a local art revision. Successful type validation alone does not
prove readable pixels, correct placement, game balance or hardware timing.

## Overlapping labels and Inspect

Use independent questions for properties that may coexist. A boardwalk can be a
built structure and locally walkable; a fungus can be scenery, a resource, or both.
Do not force material, traversal and interaction into one mutually exclusive label.
Ask walkability directly, rather than equating it with bare ground. Local support
is separate from access to an elevated surface and from actor-sized clearance.

Creative descriptors proposed by the vision model can become player-facing Inspect
text after review. The first browser study uses provisional presence/visual-fit/
no-mechanical-promise cutoffs, preserving every probability for tuning. These are
not universal acceptance thresholds for scene authorship. Avoid lore or prose that
promises rewards, animations or abilities unless an explicit supported rule exists.

Multiple labels are useful features for gameplay policies, not independent votes
whose probabilities can be summed or multiplied to manufacture certainty. A future
rule may deliberately combine fungal identity, harvest suitability, access, state
and tools. The user's fungus/harvest example motivates overlapping evidence; it is
not a settled rule that every fungus is harvestable. Current Inspect judgments do
not enable harvesting or change collision. Freeze accepted names and descriptions
with the same source/revision provenance as mechanics.

## Persistent meaning and perceptual views

Freeze accepted interpretations rather than asking Jev to rediscover a scene on
every visit. Object state advances when actions finish. Harvesting a site twice
does not create a second reward. The game's hideout/extraction save rules still
apply; this does not introduce mid-run saving.

Exposure, language and magic can select authored/generated alternate views of
the same core. A view may reveal targets or change explicitly supported affordances,
but does not reset harvested state or casually reroll item properties. Link-traded
items carry their resolved attributes and identity. Their interpretation is not
recomputed from a description on the receiving cartridge.

## Current executable experiment

`tools/jev_scene_probe.py` tests terrain, interaction categories and object boxes.
`tools/jev_scene_package.py` extends it into a frozen candidate package. Both run
offline from the cartridge's perspective, during development. Jev is an external
build-time service, not a game runtime dependency.

The package experiment currently:

- Reads the 160x144 decoded Heartwood image from the existing Hi-Color build.
- Classifies all 90 cells with local crops, ten cells per request, in nine calls.
- Retains exact decisions, input fingerprints, model and usage; cached reruns
  require no key or API calls.
- Keeps terrain and interaction categories separate. Takes Jev's selected
  categories as creative proposals instead of applying an accuracy threshold.
- Groups connected categories into provisional regions, then proposes finite
  one-cell harvest sites with stable IDs inside the frozen revision.
- Selects a test spawn in the largest ground component and derives reachable
  adjacent work cells. Unsupported and unreachable sites remain disabled.
- Produces bounded intact-to-depleted art job descriptions and versioned JSON.
  Fixed test harvest rules are 45 ticks and one fungal material per site.
- Tests the state transition and prevents a second yield after serialization.

It does **not** yet generate those art patches, implement actor-footprint collision,
choose height/occlusion rules, establish scene exits, export a native scene or
integrate the package with the real game. `runtimeReady` is explicitly false.
These are 16x16 proposal cells, not final per-pixel masks or guaranteed object
boundaries. The palette/tile proof remains in the original renderer/build; the
JSON compiler does not certify an arbitrary supplied PNG as hardware-valid.

The first decoded-image pass produced 24 proposed harvest sites in one broad
fungal region, six with reachable adjacent work cells. It used 94,627 input
tokens across nine calls. This is one generated interpretation to examine, not
a quality benchmark or a settled economy design. Original art and game files
remain unchanged. See [probe instructions and findings](art-tests/jev-scene-probe/README.md).

## Proposal → Jev → Inspect experiment

`tools/jev_scene_inspect.py` extends the same decoded Heartwood image into a
browser review with named Inspect targets and independent map labels. It uses
xAI for bounded structured proposals, then Jev 1.14 for image-grounded judgments.
Cell labels are judged without the proposal prose in their context to reduce
anchoring: walkable, fungus, harvest candidate, exposed water and built structure.
All 90 cell centers are tested with full-scene context and local crops. Object
questions separately check presence, bounds, proposed tags and Inspect prose.
Proposed anchors that disagree with the returned boxes are held for review.

Outputs include source hash, exact request fingerprints, returned model versions,
usage, raw judgments and a frozen scene revision. Calls require explicit `--run`;
cached reruns work without credentials. Browser Inspect is functional; it is not a
new native gameplay implementation. Boxes are candidate extents, not segmentation
masks; overlaps, actor clearance, exits, harvesting templates and art states remain
work to do before integration. Original scene assets remain unchanged.

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
   prose from BOTH the art description/prompt and the decoded native image. Preserve
   the brief as creative intent and the image as visual evidence; requested objects
   are not assumed to have appeared. Include amendments after art edits or native
   additions. This is an open vocabulary proposal step;
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

### Art brief input

The Inspect script accepts `--brief path/to/context.txt` (UTF-8, up to 16 KiB).
The proposal model receives the brief beside the clean decoded image and grid.
Jev object review receives it too, with an independent brief-alignment judgment.
Alignment never overrides absence, poor visual fit or an unsupported promise.
Cell-label calls remain image-only so an intent change does not silently rewrite
visual evidence or invalidate those caches. This is a deliberate separation of
intent-aware interpretation from the reusable per-cell visual measurements.

The brief is snapshotted, hashed, included in request fingerprints and the frozen
scene revision, saved beside the result, and viewable in the review UI. Omitting
it preserves existing image-only requests and cache identities. The tracked
Heartwood example combines the recorded clean-plate edit prompt with explicitly
separated later native mushroom additions; it is not misrepresented as one original
generation prompt. Future scene generation should supply its prompt directly.

## Relationships and state-change review

The next executable stage is `tools/jev_scene_review.py`. It consumes a frozen
Inspect revision, an explicit bounded list of candidate object pairs, and the
existing Heartwood harness's encoded harvest patch. It does not edit source art,
generate a replacement ROM, or automatically promote model answers into gameplay.

Relationships preserve stable endpoint IDs, direction or symmetry, independent
presence judgments, the relation probability, and review reasons. Initial types
are attachment, visibly continuous fungal growth, elevation/overlooking and a
visually continuous route. The last is only a hypothesis: a semantic relation
graph is not the navigation graph. Clearance, height transitions and reachability
remain deterministic engine checks. Unresolved Inspect objects cannot be rescued
by a high relationship score. Symmetric duplicate pairs and stale plans are rejected.

Before/after review has two separate sources of evidence:

- **Exact checks:** decode the master and patched tile bytes with the same map,
  attributes and palette schedule; validate patch identity and tile aliases;
  count all changed pixels, including any outside the authored editable footprint.
- **Visual judgments:** Jev receives both full decoded images and aligned local
  crops, plus the intended change. Independently judge the intact target, harvest
  readability, cut remnants, coherent ground/shading and preserved surroundings.
  Do not feed exact-check results or prior scores into these judgments.

The first native harvest patch changes 280 pixels within a 32x24 footprint, uses
192 bytes across 12 patterns, and changes zero exterior pixels. This proves local
patch confinement, not artistic quality or hardware timing. Jev assigned .85 to
harvest readability but only .42 to identifying the intact fans and .67 to coherent
ground/shading. The review retains that tension and holds the visual candidate;
scores are not averaged to conceal a weak prerequisite. The known harness target
is not silently linked to the Inspect mushroom proposal with unresolved bounds.

Interactive development dashboards are part of the workflow, not disposable
demos. Preserve before/after wipes, exact diffs, aligned close-ups, independent
probabilities, optional estimated bounds, threshold filters, rejected candidates,
and provenance. Keep numbers below or beside artwork instead of covering pixels.
Display filters must not mutate frozen decisions. Review data and API caches stay
local; code, plans and instructions are versioned. The cartridge stays offline.

## Human review to native prototype — October 20

The immediate goal is an automated, human-reviewed process for scaling playable
prototype ROMs and concentrating iteration on mechanics. The first end-to-end
adapter is now available in `art-tests/scene-prototype/README.md`:

1. Snapshot encoded Heartwood art, native renderer and frozen review evidence.
2. Correct walkable cells, spawn and work access in a local editor. Inspect Jev's
   overlapping labels or apply its walk proposal without treating it as approval.
3. Choose harvest duration, supply cost, starting supplies and yield.
4. Explicitly review geometry and mechanics. Freeze those exact settings.
5. Validate connectivity/budgets, generate configuration and routes, compile a
   separate native ROM, and test real inputs/state in PyBoy.
6. Play the result in Binjgb or download the ROM; retain the manifest and evidence.

Automated verification fixtures remain distinct from human-reviewed builds. Both
are prototypes, not production acceptance. The adapter uses the known encoded
harvest patch, not the unresolved model-generated mushroom box. One room/one
patch is the current boundary; multiple supported interaction types, additional
asset bundles, extraction and persistent hideout state are the next extensions.

The bounded before/after experiment compared original and stricter transition
questions on forward, identical-intact, identical-depleted and reversed pairs.
Both versions matched all four expected bands in this single-scene diagnostic.
Expected answers were not sent to the model. This is a useful control, not a
calibrated guarantee. Full-image and guided-crop mushroom localization remained
in disagreement (zero mutual box overlap), so human correction stays required.
The dashboard preserves both estimates and the original proposal.

## Further combinations to explore

These are design directions, not implemented capabilities or promises of accuracy:

1. **Learn art preferences.** Retain good/bad human labels. Let a proposal model
   suggest useful visual questions, use Jev answers as features, and test whether
   they predict held-out preferences. Avoid merely reinforcing the current look.
2. **Exposure-dependent interpretation.** Combine the decoded view with Bram's
   exposure spectrum, vocabulary and equipment to propose supported meanings or
   affordances. Freeze accepted variants against persistent core object identities.
3. **Local repair loops.** Use before/after judgments to find an unclear depletion
   state or shading seam, optionally localize it with Box, author a bounded repair,
   then recompile and recheck. Exact exterior pixels and hardware budgets remain
   hard constraints. Never rerun until a favorable score happens to appear.
4. **Adaptive questions.** Spend another crop or targeted judgment on a disagreement
   only when resolving it affects an actual decision. Bound cost, iterations and
   stopping conditions; retain failed attempts and the reason for escalation.
5. **Player-readability tests.** Compare what looks selected, depleted, traversable
   or occluded with known engine state, using actual decoded frames and sprites.
6. **Relationship-aware mechanics.** Reviewed attachment or colony candidates can
   inform explicitly designed resource groups, propagation, local reveals and
   dependency rules. The engine owns costs, persistence and causal effects.

Repeated calls measure stability, not arbitrarily precise truth. Shared model
biases, ambiguous pixels and correlated prompts can repeat the same mistake.
Use diverse relevant evidence, narrow questions, deterministic constraints and
human-reviewed held-out cases. Identical-image and reversed-state controls should
test the before/after prompts before any automated acceptance policy. Record a
valid creative interpretation once it is coherent and playable; there need not be
one objectively correct interpretation for invented scenery.

Relevant patterns: [feature discovery](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery),
[composite scoring](https://docs.typesafe.ai/patterns/composite-scoring), and
[consistency](https://docs.typesafe.ai/cookbooks/consistency_noul_cookbook).

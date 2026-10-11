# Audio, forge and boot menu — October 10, 2026

Native ROM `build/rom/the-pale-cap-atmosphere-v2.gbc`, SHA-256
`1306d064520bbbf9a7b732732f43f6fee6fde7a730b5914990f3b9e7727e28a0`.
Official build passed. Genuine emulator frames verified boot title, Controls
selection, both readable Controls pages, return to title, New Game entering the
room, cursor movement and Reveal. Frames 454–550 show all three forge cells
animating alongside Reveal. Existing recordings remain preserved; this run was
unrecorded. No queued orders leaked from title/menu confirmation.

A separate PyBoy audio comparison restored the same native save state, advanced
120 frames with and without B, and found identical stereo samples (48120 x 2).
All seven scene spell beep events were removed. A 50-second music run had nonzero
output every second (sample RMS 2.135–2.861). This verifies generated audio and
absence of the B effect, not subjective listening quality or hardware playback.
Bass now changes eight times per phrase rather than twice.

---

# First atmosphere pass — October 10, 2026

Official native and browser builds passed. Native ROM:
`build/rom/the-pale-cap-atmosphere.gbc`, SHA-256
`210273a98743261d3667baf270dfb8fa8ad84926d8a076d777ad25c3743161d4`.
The separately compiled web export has SHA-256
`9d722784f21c36ba1848b1786473334717e16d68e757f1f4c411ba08b5fa3fc3`.

Inspected genuine PyBoy frames through frame 760: ambient water/spore/cap motion,
Reveal plus traveling signals and new animation together, cursor movement, and
clean spell-overlay rendering. Source debugging confirmed active Reveal, phase
cycling, selected Reveal and zero queued orders. This was an unrecorded run;
existing retained recordings were preserved. The temporary emulator was closed.

Background analysis reports 218 unique tiles (214 allowing flips), four source
shades, and no reported violations. Native compilation accepted animation and
music assets. This is not sustained physical frame-rate or full-scene stress proof.
The original UGE score imports successfully; audible balance and loop feel have
not yet been verified by listening. Glyphs remain atmosphere, not language gameplay.

The existing browser export was refreshed successfully; reload is needed to
pick it up. Browser interaction and physical Chromatic playback remain untested.

---

# Equip feedback fix — October 10, 2026

A now commits the highlighted spell and redraws the panel without closing it.
Final native build and browser export passed. Unrecorded source-debug play
verified Bloom and Reveal each update the equipped label while the panel stays
open, holding A for 90 frames does not exit, B preserves the last equipped spell
even after highlighting another, no orders/casts leak through closing, and a
subsequent B press casts the equipped Reveal. Genuine frames were inspected.

---

# Overlay menus — October 10, 2026

Current ROM: `build/rom/the-pale-cap-panels.gbc`, SHA-256
`3e129b62391adf90a099028e36a89fa1b150f90f5d165c5622b0e44fded84e31`.
Official native and browser builds passed. Genuine PyBoy frames verified both
full-screen panels render without tile-buffer wrap/corrupted labels. Final-ROM
input tests equipped Bloom, reopened with Bloom highlighted, moved to Reveal
and cancelled (Bloom retained), equipped Reveal, opened inventory showing
Reveal, closed inventory with Start, and cast Reveal successfully. No accidental
orders were queued by menu input. Final run was unrecorded because the retained
recording quota was reached; earlier failed-render recordings remain preserved.
Browser export at the existing preview URL is updated; user reload is needed.
No new audio, world art, or forge mechanics were implemented in this pass.

---

# Cursor and context orders — October 10, 2026

Current native ROM: `build/rom/the-pale-cap-controls.gbc`.
SHA-256: `4be50b4b3e1774d9bcdbea92775bab63a0cd71f6f4c430b93234fd04e0132b85`.
Official ROM and web builds passed; valid 128 KiB GBC-only cartridge.
The existing browser export/server was updated successfully; reload the preview
for the new build. Browser automation remains unverified after the earlier policy
refusal. Physical hardware and audible playback were not tested.

Final-ROM ordinary-input recording:
`artifacts/playtests/session-c426061e-78ce-4ca1-8e1b-d2d3292b0b21`.
Verified cursor short taps and release, harvest followed by talk, rejecting an
extra A order without opening a modal or increasing the queue, resource yield
and exposure before dialogue, approach to Luma at (15,19), queue reopening after
four dialogue pages, and a subsequent ground move completing at (16,20).
Pending harvest cancellation was also exercised; see recorded variables/inputs.
Earlier iteration `session-11e3a23e-7f65-4a15-b3a1-70ae13c9f3a3` additionally
checked held-direction repeat and several FIFO ground destinations.

Path generation checks all 318 walkable actor positions form one connected
component. Banked ROM fields encode shortest terrain-safe steps for every pair.
Worker movement ignores other actors as in the previous prototype. Queue and
harvest sounds were removed from the active input/worker scripts; no listening
claim is made. Spell sounds remain unchanged.

The cursor and talk rules are provisional for rapid playtesting. Saves and
multiple workers remain out of scope.

---

## Earlier build evidence (historical)

# Cartridge playtest — 2026-10-10

Current native ROM: `build/rom/the-pale-cap-network.gbc`
SHA-256: `70be3e255f7335e23da749635783aeadc3852f8a1690deb8a05fad0e07b8584e`
Official compiler: successful, 128 KiB, GBC-only, valid cartridge checksum.
Project health: no errors or warnings. Dialogue: no line overflow; three
runtime number substitutions remain outside the static width checker.

## Final ROM: ordinary-input emulator verification

PyBoy 2.7.0 recording:
`artifacts/playtests/session-43c5c506-11b4-4e9c-b110-db82915f4c3f`.

- Moved the cursor independently of the worker, across terrain.
- Designated all eight mushroom patches; Bram completed every harvest.
- Confirmed eight resources and dwarf exposure 90 after all jobs completed.
- Cast Reveal; its lifetime reflects the played dwarf's exposure.
- Awakened roots in forge, crown, pool order; inventory fell from eight to two.
- Selected Vesper with the cursor and verified Vesper's dialogue and choice menu.
- Cancelled the choice and let Reveal expire. Inventory stayed two, all three
  roots stayed awake, exposure stayed 90, and the queue stayed empty.

`art/network-gameplay.png` is an unmodified framebuffer from this final ROM.

## Additional checks on the immediately preceding revisions

`session-7c272631-b102-4f08-8fa7-afdce6f8be24`: second job queued while the first
was active; pending cancellation and re-queue; all eight harvests; insufficient
funds; one-fungus regrowth; successful reharvest; all root orders independent.

`session-90fb5847-11f6-4b6f-a6c9-7cf56dfe0d34`: three regrown patches harvested;
inventory rose by three; exposure stopped at 100. This recording is marked
failed because cursor selection invoked the wrong NPC dialogue. The final ROM
replaces deprecated actor invocation with explicit character dialogue branches;
Vesper's corrected interaction was verified in the final recording above.

The older v2 adventure and its test recording remain available, but its pickup
and direct-movement instructions do not describe the current prototype.

## Browser and hardware limits

The official browser export was rebuilt at `build/web-network`. Its compiled
ROM identity differs from the debug native build. The existing browser preview
could not be switched: the plugin reports an unresolved recording-close
acknowledgement for its old listener. The visible tab therefore remains v2.
The old run was captured as state
`d400416ca87acd27764519f7df765d6d976f74ecd45416251be6034896d12d17` before replacement
was attempted. The user subsequently authorized discarding its progress.

No physical Chromatic test, save/load test, or audio-quality test was performed.

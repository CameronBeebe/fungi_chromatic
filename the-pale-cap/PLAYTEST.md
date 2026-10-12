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

## October 11 — first expedition ownership slice

Native ROM: `build/rom/the-pale-cap-expedition-v1.gbc`, 256 KiB, GBC-only,
SHA256 `ec649720ec13eac1eeff105dd74709b63fed2cd34ddb8bddfeb7daabdb8093d6`.
Official build passed; existing event/Node deprecation warnings remain.
Recording: `artifacts/expedition-v1-final` (PyBoy 2.7.0).

Exercised through ordinary emulator inputs: boot -> temporary hideout -> depart
-> Start -> Collect fork -> worker travel -> Bag -> Equip -> Return home ->
Store all -> Stash -> Withdraw -> Bag. The carried/equipped/stored labels changed
correctly, and withdrawal returned the fork unequipped. Home return completes
and clears its native queue order before opening the locked overlay.

`python3 tests/test_inventory.py` compiles and exercises the actual native
transfer function with a host VM adapter. Checks passed for repeated deposits
and withdrawals, equip restrictions, fungible resource conservation, overflow
retention, and bounds protection. These are state tests, not cartridge save tests.

The fork is an authored single instance (location variable 49: world/bag/stash),
with equip flag 50, home state 48, menu choice 51, and stored fungi 53. Pickup is
a queued order to walkable tile 26,14. The Start-menu shortcut was exercised;
A-at-target was added but has not yet been separately input-playtested. The
world pickup still needs an approved sprite. No existing artwork was replaced.

Limits: session-only; no cartridge saving, fork ability, capacity-based bag,
hideout improvement, extraction confirmation/loss, or illustrated hideout yet.
The screen explicitly labels session-only state and pending ability. Returning
home opens a temporary home overlay in the same scene, not a new illustrated room.

Official web export succeeded at `build/web-expedition-v1`. Opening it through
web_preview was blocked by the older listener's unresolved recording-close
acknowledgement. A close attempt also returned UNKNOWN; no force reset or server
replacement was performed. Browser gameplay for this export and physical hardware
remain unverified. The separate Gillsong art preview was not changed.

### NPC gift revision

`the-pale-cap-expedition-v2.gbc` SHA256
`29e0cc410f2636b796ef4cde0fd7a0ce661961da080ec19bab4907ea1e71642b`.
Removed Collect fork and tile coordinates from the expedition overlay. Luma's
first completed queued conversation now grants the single fork only when its
location is still unclaimed. Removed the invisible A-at-ground pickup branch.
Native emulator inputs reached Luma and displayed the gift dialogue. The existing
pickup mutation is reused as acquisition; ground pickups can later use it too.
Illustrated inspection and the save wrapper remain unintegrated. Existing preview
still serves v1 until explicitly updated; no live refresh performed in this pass.

## Integrated Root Hearth / Vermilion / home saves

Native ROM `build/rom/the-pale-cap-home-v1.gbc`, SHA256
`b709fae343d145399595a8ed161a6c7b5ef02047b6f6050836581a69e0a61ade`.
Native build passed; only pre-existing deprecation warnings. Normal GBC assets:
Root Hearth 283 unique tiles, Vermilion inspection 192, eight palettes each,
maximum four colors per tile. Sources are preserved; conversion is reproducible
with `tools/prepare_home.py`. Normal scene rendering reserves UI tile space.

`tests/playtest_home.py` ran the actual ROM with PyBoy: New Game -> illustrated
home -> depart -> Luma gift -> Bag inspection -> B back -> queued return -> stash
deposit -> Save. It stopped the emulator, retained only battery SRAM, created a
fresh emulator, and verified the home scene appears without the title menu.
Saved ownership was checked in the record; the restored stash and inspection
were visually checked. Evidence: `artifacts/home-v1-evidence/verification.json`
and numbered real framebuffers. No emulator state snapshot was used.

`tests/test_home_save.py` exercised the native record implementation with a host
SRAM adapter: roundtrip, all 55 interrupted prefixes, corruption at all 55 byte
positions, previous-record recovery, blank records and invalid ownership.
`tests/test_inventory.py` continues to cover transfer conservation and equipment
ownership. Logical recovery tests are not physical flash/power-loss guarantees.

No cartridge flash performed. Browser save/reload and physical retention require
separate checks; native cold-boot behavior is verified above.

### Gillsong inspection flow — October 11

Integrated the Vermilion study’s cyan ornament pulse into item inspection. It starts automatically; B returns as before. The fork, text, and other palettes remain static. Native emulator checked all 192 frames: exactly 245 ornament pixels animate, followed by the original rest interval. Save/load and both inspection return paths pass. Browser export rebuilt; refresh the preview to load it. Hardware animation remains untested.

## Integrated Hi-Color Hearth — October 11

Native ROM `build/rom/the-pale-cap-hicolor-home.gbc`, SHA256
`60f0e6704ff8fb9bdd7d18e144590a8b44a3da89bf17fca2104ebae436b9e06e`.
Official native build passed, CGB-only/MBC5 header valid, 256 KiB ROM and
32 KiB declared save RAM. The room payload is 8,040 bytes; no production PNG
was overwritten. Compiler output contains only the existing upstream deprecations.

Ran `tests/playtest_home.py --rom build/rom/the-pale-cap-hicolor-home.gbc
--output artifacts/hicolor-home-evidence --hicolor` with the installed PyBoy.
The actual ROM passed departure, Luma gift, both inspection return paths,
Gillsong ornament animation (245 pixels), extraction, deposit, home save and
fresh-emulator boot from battery RAM alone. The restored stash retained ownership.
Additional checks: a two-frame direction tap changed the home selection without
changing room pixels; 120 consecutive room frames stayed identical; the music
routine advanced 514 logical ticks over 120 frames both in the Hi-Color room
and in normal full-screen menus; both produced varying, non-silent emulated
audio in more than 100 of those frames. Engine soft reset restored the room.
The final room row matches the converted asset: UI palette restoration no longer
paints cyan/cream pixels along the room/menu boundary. These are timing/signal
checks, not a subjective listening assessment.

The public stepped emulator separately showed the room and functional Home
menu. The official browser export displayed the integrated room with actual
keyboard input. The plugin preview listener remains in its older unresolved
closure state, so the official export is served by a separate owned localhost
server without closing the earlier preview. Browser persistence was not tested.

Physical Chromatic output, audio quality and save retention remain unverified.
No cartridge flash was performed. Hi-Color support is limited to the static
104px home view; animated sprite highlights, streaming sound effects and link
transfers during that view require further timing work.

### Physical Hearth feedback — October 11

The plugin successfully flashed the exact native ROM above (SHA256
`60f0e6704ff8fb9bdd7d18e144590a8b44a3da89bf17fca2104ebae436b9e06e`)
to the connected Chromatic, Player 01. The write completed successfully in
24.4 seconds. The user subsequently reported: "the hearth room looks incredible."
This establishes positive user-observed appearance on hardware, not a measured
frame-timing, audio, menu-boundary or save-retention check. Those remain open.
No computer screen/audio recording or physical capture was used. The user also
identified the overworld's visuals and gameplay as the next overhaul priority.

### Hearth transition fixes — October 11

The user reported the old blocky Hearth flashing before the richer image and
snow/garbled graphics while moving between home and the expedition. The original
scene explicitly faded in the fallback art; stopping Hi-Color also restored
ordinary palettes over the still-visible Hi-Color tilemap. Removed that entry
fade and now prepare renderer/menu changes under black before revealing them.
LCD stays enabled during the tile upload to avoid a white LCD-off flash.

An extended check also caught occasional palette corruption: the VBlank music
callback could delay LYC 152 until line 153. Music now runs after the rendered
image, once the real stack and ROM bank have been restored.

Fixed native ROM: `build/rom/the-pale-cap-hicolor-transition.gbc`, SHA256
`f10da0c902c8786cbd15cd09c7f05ed218cf52c7c8f1460263e1caf4d2f6a487`.
The new regression fails against the previously flashed ROM on entry frame 4.
The fixed ROM passes 1,550 transition frames across new game, departure,
extraction, menu return and battery cold boot; 3,600 consecutive room frames
remain identical with music active. Music counts are 514/515 ticks per 120 frames
in room/menu respectively, within the expected fractional-clock phase range.
The complete item/inspection/deposit/save/soft-reset flow also passes. Public
stepped emulator samples separately show menu -> black -> complete Hearth.
These fixes have not yet been flashed or verified on physical hardware.

The scene now loads a uniform single-tile backing instead of the original Hearth
illustration. Build symbols confirm no `bg_root_hearth` image payload is linked;
the source PNG is preserved unchanged. Only the Hi-Color Hearth illustration is
used in the game. The padded cartridge size remains 256 KiB.

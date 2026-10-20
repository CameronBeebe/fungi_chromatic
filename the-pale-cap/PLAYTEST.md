# Validation record

Hardware observations, emulator assertions and host-side tests establish different
things. Generated ROMs/screenshots are local ignored artifacts; hashes identify
which binary each recorded result describes. This is not a claim that every
subsequent source revision has been flashed.

## Integrated game: Hi-Color Hearth and persistence

Latest recorded integrated transition build, 256 KiB:
`build/rom/the-pale-cap-hicolor-transition.gbc`

SHA-256: `f10da0c902c8786cbd15cd09c7f05ed218cf52c7c8f1460263e1caf4d2f6a487`

The regression catches the earlier fallback-art flash on entry frame 4. The fixed
build passed 1,550 transition frames across New Game, departure, extraction,
menu return and battery cold boot. 3,600 consecutive room frames stayed identical
with music active. Music counts were 514/515 logical ticks per 120 frames in
room/menu, within fractional-clock timing. Item inspection, stash deposit, save,
cold boot and soft reset passed. The old Hearth payload is not linked; its source
PNG remains preserved. The room payload is 8,040 bytes above the home menu.

The preceding integrated build was:
`60f0e6704ff8fb9bdd7d18e144590a8b44a3da89bf17fca2104ebae436b9e06e`

That binary passed extraction, Luma's gift, both inspection return paths,
245-pixel ornament animation, ownership retention and fresh-emulator boot from
battery RAM alone. A two-frame direction tap changed selection without altering
room pixels. Room/menu audio was non-silent and varying. These are timing/signal
checks, not a subjective audio-quality assessment.

### Physical observations

The integrated Hearth was flashed to a Chromatic and its visual appearance was
positively evaluated. Initial playtesting exposed old-art and garbled transition
flashes; subsequent hardware playtesting reported clean results after the fix.
The six-view static overworld gallery was also displayed on hardware. Those
observations do not validate the later interactive Heartwood harness.

Physical battery retention, power-loss recovery, audio quality and individual
menu-boundary checks still need dedicated tests. No hardware photo/video is
included yet. Emulator evidence is not presented as physical footage.

### Reproduce native playtests

Install PyBoy and Pillow, build the matching integrated ROM with debug symbols,
and run from the repository root:

```sh
python3 the-pale-cap/tests/playtest_home.py \
  --rom the-pale-cap/build/rom/the-pale-cap-hicolor-transition.gbc \
  --output the-pale-cap/artifacts/hicolor-transition-evidence --hicolor
```

The test retains battery SRAM for cold boot, not an emulator state snapshot.
It records ROM identity and real framebuffers. It needs matching generated
Hi-Color assets and debug symbols. It is separate from the offline unit suite.

## Standalone Heartwood harness

Native ROM SHA-256:
`a42db8e45e41ec726e6663a7974bc018f07c021997fe5aa13138479a374f1ebc`

The 64 KiB standalone ROM passed cursor/pin/arrival-center alignment, both screen
corners, foreground visibility, two-frame cursor response, FIFO harvesting,
blocked-target rejection, single yield, help/reset and persistent depleted state.
Across 841 checked frames, scenery outside sprite rectangles, patch footprints
and the status row stayed unchanged. Browser emulation displayed the native ROM.
B is labeled REVEAL TEST; it has no gameplay benefit. No physical check of this
interactive build is recorded. See its [README](art-tests/heartwood-playable/README.md).

## Reviewed scene adapter — October 20

Three separate 64 KiB automation fixtures passed actual PyBoy input/state checks:

- Default: 60-tick harvest, +2 loot, cost 1; SHA-256
  `e30b2961ada603e569df5bd920c04c4ffd0b0f15cab42ec855ee6e591e2d8fc0`.
- Alternate spawn, 120-tick harvest, +7 loot, cost 2; SHA-256
  `8d5ba2f534cfdd7933895fe0778fa8a3f6f7b91bae3dedbeb2a17cdbab4740a6`.
- Unaffordable work rejection; SHA-256
  `6dab612c74aae2bb78bad3c064856482fb7d7e62464db29e32d149fb2e1c213d`.

Checks cover spawn, traversed foot cells, duration, spending/yield, duplicate
harvest rejection, help-menu revisit persistence and reset. Browser checks cover
numeric validation, Jev proposal, blocked spawn, undo and real native rendering.
Wrong-origin and missing-review requests were rejected by the local server.
Automation fixtures are not human approvals. No physical flash was performed.

## Offline state and tooling tests

`make test` compiles the actual C save/inventory code against small host adapters,
then discovers all scene-tool unit tests. Save checks cover roundtrip, all 55
interrupted prefixes, corruption at every record byte, fallback, blank records
and invalid ownership. Inventory checks cover repeated transfers, equipment,
capacity and conservation. Scene tests cover schemas, probabilities, cache and
snapshot identity, exact pixel bounds, route constraints and approval gates.

These tests require no model calls, ROM or private artwork. Logical recovery does
not prove electrical power-loss behavior. CI runs this suite and formatting;
full integrated-game compilation and physical hardware checks are separate.

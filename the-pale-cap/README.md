# The Pale Cap

An experimental, offline Game Boy Color game: move a cursor, queue
harvests for the played dwarf, spend fungi to grow the network, and reveal a
neon mycelial layer. The played dwarf's spore exposure determines your view.

## Play

With a valid compatible save, boot opens the hideout directly. Otherwise boot
opens New Game / Controls; New Game enters the hideout. Use up/down and A.

- D-pad / arrows: move the selection cursor across the map.
- A / Z: queue movement on empty walkable ground, or harvesting on a mushroom.
  Press a pending mushroom again to cancel its harvest.
- A on a character: queue a conversation after existing orders. Further orders
  are ignored until the conversation finishes.
- B / X: cast the selected spell at the cursor.
- Select / Shift: open the spell overlay. Up/down highlights, A equips in place, B closes.
  Opening the menu keeps the current spell equipped.
- Start / Enter: open the expedition bag/status overlay, including item
  inspection/equipment and queued return home. Home provides bag, stash,
  deposit/withdraw, save and departure actions. Follow the on-screen prompts.
- A: advance dialogue and confirm choices.

Bram walks and works independently. Resources arrive when he finishes harvesting.
Bloom costs two fungi to awaken a root. Cast at an awakened root to regrow its
harvested patches for one fungus. Reveal is free in this prototype. Awakening
all three roots makes Vesper available during Reveal.

Open `project.gbsproj` in GB Studio 4.3.2 to edit/play; Export ROM creates
`build/rom/game.gb`. Build outputs are local and ignored by Git. No hardware or
developer code is required for emulator play. See the [setup walkthrough](../docs/GETTING_STARTED.md).
Saving is available only at home after extraction. Saves use version/checksum
validation and two alternating records. The latest home save is restored on
boot; there is no mid-run resume. No API keys, Wi-Fi, LLM calls, or Jev calls are
required. Physical cartridge retention still needs separate testing.

Luma grants a single authored Gillsong fork. It can be inspected, equipped,
deposited and withdrawn; its gameplay ability is still pending. Inspection uses
the approved Vermilion study with animated cyan ornament. The illustrated Root
Hearth uses a 104-pixel-high Hi-Color image above its functional home menu.
Full-screen bag/stash/save menus and the expedition restore normal engine
rendering. The [Hi-Color study](art-tests/hearth-hicolor/README.md) remains a
separate comparison demo. The game integration uses an 8,040-byte room payload;
the compiled ROM remains 256 KiB in the tested build.

See [TODO.md](TODO.md) for the living backlog,
[DESIGN.md](DESIGN.md) for agreed rules and provisional mechanics, and
[PLAYTEST.md](PLAYTEST.md) for actual validation and its limits. In particular,
spell casting is still immediate; movement, harvesting and talking use a
16-order FIFO queue. These controls are provisional playtest choices.

## Native art and source

The project uses a scrolling 256 x 224 room in a genuine 160 x 144 GBC viewport,
seven background palette slots plus a reserved UI palette, native sprite art,
animated root tiles, and a traveling signal. Original assets remain available.
`tools/draw_grotto.py` and `tools/draw_network.py` contain the native pixel drawing
recipes. Resource scripts and collision/palette assignments live in `project/`.
Changing the map requires checking worker routes as well as graphics.

The first atmosphere pass adds animated water, spores, fungal pulses, embers and
Reveal glyphs, plus an original looping score, *A Grammar of Spores*. Source
recipes are `tools/draw_atmosphere.py` and `tools/compose_whisper.py`. Glyphs are
currently atmospheric; language-based interactions are tracked in TODO.md.

## Dependencies and notices

GB Studio and GBDK build the native game. `uv sync --locked` installs the pinned
Python art/test dependencies; `--extra demo` adds PyBoy for native emulator
automation. Host state tests also require a C compiler.
See [third-party notices](../THIRD_PARTY_NOTICES.md) before redistributing source,
ROMs or preview files. Preserve the existing GB Studio MIT `LICENSE`.

To regenerate the integrated Hi-Color arrays, run
`uv run --locked python tools/prepare_hearth_hicolor.py`. It packages the checked-in converter
outputs using tile banks that preserve GBVM's font allocation. Rebuild the study
first only when intentionally changing its source/conversion. The integration
test accepts `--rom`, `--output`, and `--hicolor`; the last option checks room
stability, short direction taps, music cadence/output and soft reset in addition
to the full extraction/save/cold-boot loop. It needs the matching debug symbols
next to the ROM. See PLAYTEST.md for the exact tested build and limitations.

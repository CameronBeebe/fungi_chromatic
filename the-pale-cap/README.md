# The Pale Cap

An offline Game Boy Color prototype of Fungi Fortress: move a cursor, queue
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

Open `project.gbsproj` in GB Studio to edit. The current integrated cartridge is
`build/rom/the-pale-cap-home-v1.gbc`; build outputs are local and ignored by Git.
Saving is available only at home after extraction. Saves use version/checksum
validation and two alternating records. The latest home save is restored on
boot; there is no mid-run resume. No API keys, Wi-Fi, LLM calls, or Jev calls are
required. Physical cartridge retention still needs separate testing.

Luma grants a single authored Gillsong fork. It can be inspected, equipped,
deposited and withdrawn; its gameplay ability is still pending. Inspection uses
the approved Vermilion study with animated cyan ornament. The illustrated Root
Hearth currently uses standard GBC palettes. The richer
[Hi-Color study](art-tests/hearth-hicolor/README.md) is a separate rendering demo,
not the main game ROM.

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

GB Studio and GBDK build the native game. Python art tools require Pillow;
the newer conversion and seam-audit tools also require NumPy. Native emulator
automation uses PyBoy; host state tests require Python and a C compiler.
See [third-party notices](../THIRD_PARTY_NOTICES.md) before redistributing source,
ROMs or preview files. Preserve the existing GB Studio MIT `LICENSE`.

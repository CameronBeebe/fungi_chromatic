# The Pale Cap

An offline Game Boy Color prototype of Fungi Fortress: move a cursor, queue
harvests for the played dwarf, spend fungi to grow the network, and reveal a
neon mycelial layer. The played dwarf's spore exposure determines your view.

## Play

Boot opens New Game / Controls. Use up/down and A; Controls has two pages.

- D-pad / arrows: move the selection cursor across the map.
- A / Z: queue movement on empty walkable ground, or harvesting on a mushroom.
  Press a pending mushroom again to cancel its harvest.
- A on a character: queue a conversation after existing orders. Further orders
  are ignored until the conversation finishes.
- B / X: cast the selected spell at the cursor.
- Select / Shift: open the spell overlay. Up/down highlights, A equips in place, B closes.
  Opening the menu keeps the current spell equipped.
- Start / Enter: open the inventory/status overlay. A, B, or Start closes it.
- A: advance dialogue and confirm choices.

Bram walks and works independently. Resources arrive when he finishes harvesting.
Bloom costs two fungi to awaken a root. Cast at an awakened root to regrow its
harvested patches for one fungus. Reveal is free in this prototype. Awakening
all three roots makes Vesper available during Reveal.

Open `project.gbsproj` in GB Studio to edit. The current cartridge is
`build/rom/the-pale-cap-atmosphere-v2.gbc`; the previous adventure version remains
`build/rom/the-pale-cap-v2.gbc`. Progress lasts for the current run; saves are not
implemented. No API keys, Wi-Fi, LLM calls, or Jev calls are required.

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

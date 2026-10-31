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

## Co-playing NPC prototype

Moss starts in Bram's party; Pip starts independently. Both use the same native
agent executor. They find nearby unclaimed mushrooms, walk the real navigation
routes, reserve and harvest patches, and carry their own fungi. Player orders
and NPC claims cannot harvest the same patch twice. This build has two agent
slots and eight existing resource sites; it is a bounded prototype of the shared
system, not an unlimited NPC simulation. Luma and Vesper retain their authored
story interactions.

During an expedition, **START → Companions → Moss / Pip** opens conversation and
plans: follow Bram, forage, wait, share, join, leave, or give a fungus. Transfers
and joining require proximity. Joining and leaving change party membership,
not the underlying action rules. A gift is remembered and increases trust;
trusted companions keep one fungus before sharing, rather than two. Their bags,
intentions, gift/share memories and trust persist through extraction and home
saves. Version 1 home saves still load; the next save writes version 2.

The cartridge currently uses offline decisions and short authored dialogue.
There is **no Wi-Fi or on-cartridge LLM inference** in this change. A host adapter
can choose intentions with xAI tool calls and submit them to the actual ROM;
model speech is retained in its host report, not displayed as cartridge dialogue.
The adapter defaults to offline mode and does not make requests unless `--run`
is explicit. Free-form on-cartridge conversation and richer narrative arcs are
still future work.

After a native build with matching debug symbols, run this fresh-save emulator
demo from the repository root (requires the `demo` extra):

```sh
uv run --locked --extra demo python the-pale-cap/tools/agent_bridge.py \
  --rom the-pale-cap/build/rom/the-pale-cap-agents.gbc \
  --prompt follow --output the-pale-cap/artifacts/agents/bridge
```

For a live model choice, set `XAI_API_KEY`, add `--run`, and use a natural-language
prompt such as `--prompt "Stay close, but keep a fungus for yourself."`. This is
a single-decision headless host demo: simulation pauses during the request, then
the ROM applies the response and continues. It copies the ROM into temporary
storage and does not touch your battery save. API behavior has been tested with
mocked responses; no live paid model call or physical hardware test was performed.

### Decision interface for the Wi-Fi prototype

The receiver must resolve **named variable aliases from this build's symbols**,
not assume project IDs are RAM addresses or contiguous. Read Moss/Pip state
from project IDs 61–72 / 73–84: x, y, intent, bag, trust, gifts, shared, revision,
target, progress, joined, initialized. Only send the agent's own state and nearby
patches; the host adapter demonstrates that observation shape.

The command mailbox is: ID 89 slot (0/1), 87 command, 88 expected agent revision,
90 sequence, 91 consumed sequence, 92 status. Commands are 1 follow, 2 forage,
3 wait, 4 share, 5 join, 6 leave. Player gifts (7) are local-only. Transport must
stage a complete packet, commit its sequence last atomically against simulation,
and allow at most one outstanding request. Sequences strictly increase within
one boot session; do not reuse packets across boots or allow 16-bit rollover.
A hardware transport must supply its own connection/session framing.

Status 1 means accepted, 2 stale/replayed/invalid command, 3 currently unavailable.
An invalid slot is not consumed: validate it at the transport boundary. Accepted
intentions continue without more packets; normal play never waits for a model.
The native executor owns paths, harvest reservations, proximity, capacity and
resource changes. Remote decisions cannot set inventory, trust or coordinates.
The current adapter pauses PyBoy before writes; hardware transport is intentionally
left to the Wi-Fi work. Both NPCs run local controllers on a bounded cadence;
there is not yet a distant-world simulation or background model scheduler.

Verification (from repository root):

```sh
make test
uv run --locked --extra demo python the-pale-cap/tests/playtest_agents.py \
  --rom the-pale-cap/build/rom/the-pale-cap-agents.gbc \
  --output the-pale-cap/artifacts/agents/playtest
uv run --locked --extra demo python the-pale-cap/tests/playtest_home.py \
  --rom the-pale-cap/build/rom/the-pale-cap-agents.gbc \
  --output the-pale-cap/artifacts/agents/home --hicolor
```

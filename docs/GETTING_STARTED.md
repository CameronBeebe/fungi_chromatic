# Run the experiment locally

The integrated game and the Heartwood authoring experiment are separate ROMs.
Both can run in emulators. You do not need ModRetro hardware, a developer code,
a Codex plugin, or model API credentials for these paths. Nothing below flashes
hardware. Initial dependency/tool downloads require internet access; after setup,
the examples and tests run offline.

Commands below use a macOS/Linux shell, Git and [uv](https://docs.astral.sh/uv/getting-started/installation/).
macOS has local validation; Ubuntu runs in CI. Native Windows setup is not
validated. Use the upstream GB Studio desktop application to explore the game
on Windows; the Python/native study workflow has not been certified there.

## Set up Python and run tests

From the cloned repository root:

```sh
uv sync --locked
uv run --locked python scripts/test.py
make format-check
```

`.python-version` selects Python 3.12. `uv.lock` pins direct and transitive
packages; `--locked` rejects inconsistent dependency metadata rather than
silently changing versions. No virtual-environment activation is required.
`pyproject.toml` is the dependency source of truth; use `uv lock` deliberately
when updating dependencies, and commit the lockfile with the change.

The tests compile save/inventory C code with `cc`, then run offline Python
unit tests. Install Apple's Command Line Tools on macOS or a C build toolchain
on Linux if `cc` is missing. No Game Boy compiler or emulator is needed here.

## Inspect and edit the offline scene example

```sh
uv run --locked python the-pale-cap/tools/scene_prototype.py example --serve
```

Open the printed `http://127.0.0.1:.../` URL in your browser. The port and session
path are generated each time. Stop the server with Ctrl+C when finished.

1. Hover cells to see recorded Jev probabilities beneath the image. These are
   historical model outputs, not fresh inference or ground truth.
2. Toggle the grid, walkable mask and Jev overlay. Paint walkable/blocked cells
   or move the spawn/work point. Orange marks the fixed harvest patch.
3. Change work duration, starting supplies, cost or loot yield. Invalid geometry
   or values disable the build button. The authored mask is the starting point.
4. Use **Export draft** to keep settings without compiling. To build, install
   the native prerequisites below, review both confirmations, and choose
   **Approve & build prototype**.

The checked-in example is about 100 KiB of selected art and evidence, not the
concept portfolio. The command snapshots current engine source into ignored
`the-pale-cap/art-tests/scene-prototype/build/`; it never alters the example or
overwrites edited snapshots. Existing generated runs remain there. Candidate
metadata records its seed and source hashes. See [example provenance](../examples/heartwood/README.md).

## Compile and play the Heartwood experiment

Download [GBDK-2020 4.5.0](https://github.com/gbdk-2020/gbdk-2020/releases/tag/4.5.0)
for your OS/CPU and extract it. Set `GBDK_PATH` to the absolute directory containing
`bin/lcc` and `bin/png2hicolorgb` (not to `bin` itself). This is a public compiler
release; no ModRetro account is involved.

```sh
export GBDK_PATH=/absolute/path/to/gbdk
uv sync --locked --extra demo
uv run --locked --extra demo python the-pale-cap/tools/scene_prototype.py example --verify --serve
```

The optional `demo` dependency installs PyBoy for actual-ROM tests. Keep
`--extra demo` on commands that build or emulator-test; ordinary `uv run` may
synchronize an environment without that optional package.

`--verify` compiles and exercises the default scene before starting the server.
The editor then offers **Play ROM**, **Download ROM**, and verification links.
The first result is explicitly an automation fixture, not human approval.
After you edit and approve settings, a separate result records that review.

In the browser player: Enter opens/closes help, arrows move the cursor, Z queues
walking or harvesting, X toggles the reveal visualization, and Shift resets the
experiment. Queue a harvest on the amber patch; Bram walks to it, spends supplies,
and adds loot after working. This room has no hideout, extraction or save system.

Compiler logs, reviewed JSON, ROMs and before/after emulator frames stay in ignored
`build/` directories. If compilation fails, check `GBDK_PATH` and the generated
`compiler.log`. Never place API keys in these files or the dashboard.

## Play and edit the integrated game

Install [GB Studio 4.3.2](https://github.com/chrismaltby/gb-studio/releases/tag/v4.3.2).
Open `the-pale-cap/project.gbsproj` and click **Play**. Keep the included
`plugins/colony-controls` engine extension alongside the project. It uses native
Game Boy Color features; newer GB Studio versions are not yet validated here.

GB Studio supplies its own game build environment; the Python uv environment
is for this repository's tools and tests. **Export ROM** writes
`the-pale-cap/build/rom/game.gb`; **Export Web** creates `the-pale-cap/build/web`.
A `.gb` extension does not imply monochrome: the ROM's header selects GBC mode.
See the [official build guide](https://www.gbstudio.dev/docs/build/) and
[game controls](../the-pale-cap/README.md).

The integrated project was rebuilt from tracked files with the official 4.3.2
CLI on October 21, 2026. Emulator checks passed new game, NPC gift, animated item
inspection, extraction, stash transfer, home save and cold boot. This does not
claim a fresh desktop GUI test, physical cartridge test or validation of every
spell/encounter.

## Build the smaller rendering comparison

```sh
sh the-pale-cap/art-tests/hearth-hicolor/build.sh
uv run --locked python -m http.server 8000 --bind 127.0.0.1 --directory the-pale-cap/art-tests/hearth-hicolor/web
```

With `GBDK_PATH` set, the script builds `bin/hearth-hicolor.gbc` and updates the
browser player's ROM copy. Open `http://127.0.0.1:8000/`. Z selects Hi-Color, X
selects standard palettes, and Enter toggles the menu study. This comparison is
not the integrated game and its menu entries are demonstrations.

## Automated builds and scope

The **Offline tests** GitHub Actions workflow checks the locked environment,
host/unit tests and Python formatting. Its native-demo job downloads the official
GBDK 4.5.0 Linux archive with a pinned SHA-256, compiles the Hearth study and the
Heartwood example, and runs the Heartwood ROM in PyBoy. Successful runs attach
ROM/player/verification artifacts for those standalone experiments, with license
notices. Downloading Actions artifacts may require a GitHub login. The integrated
GB Studio game is currently validated locally, not by that CI job.

Live proposal/Jev generation is separate: it needs provider credentials and an
explicit `--run`. Other historical art studies may still need untracked source
art. The offline example is deliberately self-contained; it does not make those
studies or arbitrary new scenes reproducible automatically.

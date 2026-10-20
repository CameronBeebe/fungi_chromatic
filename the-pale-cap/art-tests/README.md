# Native studies and development tools

These directories are not levels in the integrated game. Their READMEs state
what each ROM or tool actually demonstrates and what remains unverified.

## Active reference studies

- [hearth-hicolor](hearth-hicolor/README.md): finished standalone full-screen and
  cropped-menu rendering comparison. Rebuilds from tracked inputs with GBDK_PATH.
  Its renderer is also adapted by the integrated game's home scene.
- [gillsong-refinement](gillsong-refinement/README.md): finished normal-color
  inspection/ornament study. Required baseline/art headers remain tracked because
  `tools/prepare_home.py` uses them. Node/Sharp and native tool dependencies apply.
- [heartwood-playable](heartwood-playable/README.md): interactive one-room GBDK
  harness for movement, local art patches and harvesting. It requires the local
  original concept PNG (or an explicitly supplied replacement); missing input
  produces an early actionable error, not a partial build.

## Development pipeline

- [jev-scene-probe](jev-scene-probe/README.md): proposals, judgments, relationships,
  before/after evidence and review dashboards. APIs are development-time only.
- [scene-prototype](scene-prototype/README.md): human-reviewed map/economy settings
  compiled into a separate Heartwood ROM. This is not integrated-game content yet.

## Historical references

`gillsong/` preserves the original art conversion and source; the refinement is
the preferred study. Its original concept sheet is local and ignored.
`overworld-gallery/` preserves the static six-view hardware comparison builder;
it requires six local concept images. `root-hearth-conversion/` retains recipe
configs, comparison images and notes, not the six intermediate output trees.
These intentional source/reference files have not been deleted for tidiness.

Generated ROMs, emulator saves/logs, build folders and API caches are ignored.
Required build inputs and licensed Binjgb/GB Studio player dependencies remain
tracked. The Hearth's generated-looking arrays include required standard-mode
and font inputs; do not delete them without a replacement generator.
The broad `concept-art/` portfolio stays local.

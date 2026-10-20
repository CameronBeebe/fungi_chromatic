# Roadmap

Updated October 20, 2026. Open work only; implemented features live in
[README.md](README.md), design decisions in [DESIGN.md](DESIGN.md), and validation
in [PLAYTEST.md](PLAYTEST.md). These are priorities, not promised release scope.

## Next playable milestone

- [ ] Human-playtest the reviewed Heartwood ROM: visual clearance, responsive
  orders, work access, feedback and useful harvest timing/cost/yield.
- [ ] Generalize the scene bundle to another room: master art, bounded state
  patches, navigation, layering, stable object IDs and transition points.
- [ ] Support multiple interaction sites and explicit effect types, including
  Inspect text, costs/rewards and persistent depleted states.
- [ ] Connect reviewed scenes to expedition → extraction → hideout → save.
  Keep standalone harnesses distinct until that integration is verified.
- [ ] Give Gillsong one useful, legible ability with costs and persistent effects.
- [ ] Prototype one exposure/language encounter with a meaningful world response;
  clarify the overlap among learned words, exposure and spell effects.

## Reliability and authoring

- [ ] Expand the scene review dataset across biomes; retain human corrections,
  disputed bounds, before/after controls and failed candidates.
- [ ] Make fixed/dynamic art and sprite layering consistent without losing
  readable walkable space or interaction targets.
- [ ] Test menu boundaries, audio quality and physical save retention separately
  on Chromatic hardware; retain ROM identities with results.
- [ ] Define run abandonment, equipment loss and autosave rules before adding
  departure records. Never allow a reload to duplicate extracted resources.
- [ ] Add a fresh integrated-game build to automated validation when a portable
  GB Studio toolchain setup is established. Current CI runs offline host tests.

## Later gameplay experiments

- [ ] Hideout construction/cultivation with a small number of useful stations.
- [ ] Fungal exposure bands or spectra, proximity/decay rules, distinct biomes
  and view-dependent opportunities on one persistent world.
- [ ] Turn-based encounters that pause exploration and restore it consistently.
- [ ] Stable item imprints, bounded effects, durability and contextual trade
  recommendations; balance a few meaningful stats before broad generation.
- [ ] Link-cable trading: compatibility, mutual confirmation, recovery and saves.
- [ ] Live generated content and proposed Wi-Fi/firmware, outside the offline MVP.

## Publication decisions

- [ ] Choose a project-wide license for original code/art.
- [ ] Resolve the Hi-Color ISR's source-header/distribution-notice ambiguity;
  see [third-party notices](../THIRD_PARTY_NOTICES.md).
- [ ] Add real Hearth hardware footage under `docs/media/`.
- [ ] Decide separately whether public release should use fresh history, and
  whether to delete merged remote branches. Cleanup does neither automatically.

# SNAP-T2 SnapATAC2 Preprocessing Notes

- Use a SnapATAC2-style path: load the declared single-cell data, preserve
  source-paper preprocessing assumptions, and run dimensionality reduction
  before downstream clustering or artifact reporting.
- Keep objective logs separate from interpretation. The scorer expects
  machine-readable artifacts and ARI/NMI or pre-registered proxy plus runtime/memory.
- Do not expose scorer-only labels, thresholds, or post-run metric files to the
  model condition context.

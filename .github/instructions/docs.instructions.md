---
applyTo: "docs/**,zensical.toml"
---

# Documentation Instructions

- Documentation is in English; the decision log `TRACCIAMENTO_MODIFICHE.md` is the Italian source of truth.
- Every page added under `docs/` must be listed in the `nav` of `zensical.toml`, or the build drops it.
- Compliance pages (`docs/compliance/`) must match the code: routing matrix = `OversightManager.livello_dichiarato()`,
  thresholds = `train_baseline.SOGLIE`, alert thresholds = `BiasDetector` defaults.
- Reference decisions by ID (`D-NN`) and link to `decisions/index.md`.
- Use admonitions (`!!! warning`, `!!! info`) for limits and notes, Mermaid for flows.
- Theme colors only through `--enel-*` tokens in `docs/stylesheets/extra.css`.

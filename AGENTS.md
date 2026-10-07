# AGENTS.md

Guidance for AI coding agents working in the **EnerGuard** repository.

## Project Overview

A predictive-maintenance model for grid assets with an EU AI Act Art. 14
human-oversight layer, built for the AI Human Oversight Hackathon. The
system is classified **high risk** (Annex III, critical infrastructure).

- Python modules at the root (`app.py`, `oversight_manager.py`,
  `bias_detector.py`, `explainer.py`, `audit_logger.py`, `train_baseline.py`,
  `utils_io.py`)
- `docs/` — Zensical documentation site (English)
- `TRACCIAMENTO_MODIFICHE.md` — decision log D-01..D-40 (Italian)
- `.github/` — CI/CD, templates, Copilot customizations

## Setup & Build Commands

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-docs.txt
python train_baseline.py          # model.joblib + predizioni.csv
streamlit run app.py              # dashboard on :8501
python test_llm.py                # explanation smoke test
zensical serve                    # docs on :8000
zensical build --clean            # docs to site/
```

## Governance

All work complies with **OP35** and **OP36** (see
`.github/copilot-instructions.md`) and with the
[Enel OSPO](https://github.com/ENEL-GICT-PTG/OSPO) repository rules.

## Critical Conventions

- **Language:** code identifiers, comments and the decision log are in
  Italian (hackathon constraint); documentation in `docs/` is in English.
- **Decisions:** any change to thresholds, routing, alerts or explanations
  needs a new `D-NN` entry in `TRACCIAMENTO_MODIFICHE.md`, a `DECISIONE:`
  comment in the code, and an update to the matching page in
  `docs/compliance/` or `docs/decisions/`.
- **Routing:** `OversightManager.route()` and `livello_dichiarato()` must
  implement the same matrix as `docs/compliance/oversight-declaration.md`.
- **Execution:** only `OversightManager._esegui` may execute an action.
- **Audit:** every state transition calls `AuditLogger.log`.
- **New docs pages** must be registered in the `nav` of `zensical.toml`,
  otherwise the build silently drops them.
- **SPDX header** on every source file:
  `# SPDX-License-Identifier: Apache-2.0`.

## Copilot Customizations

| Type         | Location                                     | Purpose                               |
| ------------ | -------------------------------------------- | ------------------------------------- |
| Instructions | `.github/copilot-instructions.md`            | OP35/OP36 rules, coding standards     |
| Instructions | `.github/instructions/*.instructions.md`     | Path-scoped rules (docs, oversight)   |
| Agents       | `.github/agents/*.agent.md`                  | Technical writer persona              |
| Skills       | `.github/skills/enel-design-system/SKILL.md` | Enel Design System for the docs theme |

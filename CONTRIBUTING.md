# Contributing to EnerGuard

Thank you for your interest in contributing. This project follows the
[Enel OSPO](https://github.com/ENEL-GICT-PTG/OSPO) guidelines and the
OP36 design-by-default requirements.

## Code of Conduct

By participating you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

1. Open an issue describing the bug or feature (use the templates).
2. Fork the repository and create a branch named `<type>/<description>`,
   for example `feat/override-alert` or `fix/sla-escalation`.
3. Make your changes and run the checks below.
4. Commit using [Conventional Commits](https://www.conventionalcommits.org/):
   `type(scope): description`.
5. Open a pull request and fill in the template.

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-docs.txt
cp .env.example .env   # optional, only for LLM explanations
python train_baseline.py
```

## Checks Before a Pull Request

```bash
python -m compileall -q .              # syntax
python train_baseline.py               # model and fairness report
python test_llm.py                     # explanation engine
zensical build --clean                 # documentation site
```

## Project Rules

- **Decisions are documented.** Every design choice that affects oversight,
  thresholds or fairness gets an ID (`D-NN`) in
  [TRACCIAMENTO_MODIFICHE.md](TRACCIAMENTO_MODIFICHE.md) and a
  `DECISIONE:` comment in the code.
- **One execution path.** Every action must go through
  `OversightManager._esegui`. Do not add alternative execution paths.
- **Routing matrix in sync.** If you change `route()`, update
  `livello_dichiarato()` and the
  [oversight declaration](docs/compliance/oversight-declaration.md):
  KPI A6 must stay at 100%.
- **Every state transition is logged** through `AuditLogger`.
- **No secrets in code.** Configuration goes in `.env`; update
  `.env.example` when you add a variable.
- **License headers.** New source files start with:

  ```python
  # SPDX-License-Identifier: Apache-2.0
  # Copyright (c) 2026 Enel SpA
  ```

- **Dependencies.** Check the license of every new dependency (OP36 4.15).
  AGPL, SSPL and GPL-3.0 are blocked by the CI license gate.

## Documentation

Documentation lives in `docs/` and is built with
[Zensical](https://zensical.org/). New pages must be added to the `nav` in
`zensical.toml`, otherwise they are not published.

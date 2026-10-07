# Contributing

The full guide is in
[`CONTRIBUTING.md`](https://github.com/GuidoMerliniEnel/ai-act-hackaton/blob/main/CONTRIBUTING.md).
It follows the [Enel OSPO](https://github.com/ENEL-GICT-PTG/OSPO) best practices.

## Workflow

1. Open an issue using the bug or feature template.
2. Create a branch `<type>/<description>` (e.g. `feat/override-alert`).
3. Commit with [Conventional Commits](https://www.conventionalcommits.org/):
   `type(scope): description`.
4. Open a pull request; the template includes the oversight and OP36
   checklists.
5. CI must pass: build, smoke tests, docs build, security and license gates.

## Rules that protect compliance

!!! do "Do"
    - Record every design choice as `D-NN` in `TRACCIAMENTO_MODIFICHE.md`
      and with a `DECISIONE:` comment, then update [Decisions](../decisions/index.md).
    - Keep `route()`, `livello_dichiarato()` and the
      [oversight declaration](../compliance/oversight-declaration.md) aligned.
    - Log every new state transition through `AuditLogger`.
    - Add `# SPDX-License-Identifier: Apache-2.0` to new source files.
    - Register new docs pages in the `nav` of `zensical.toml`.

!!! dont "Don't"
    - Add a second execution path besides `OversightManager._esegui`.
    - Commit `.env`, API keys or production data.
    - Add dependencies under AGPL, SSPL or GPL-3.0.

## Copilot customizations

| Type         | File                                                  |
| ------------ | ----------------------------------------------------- |
| Instructions | `.github/copilot-instructions.md`                     |
| Instructions | `.github/instructions/oversight.instructions.md`      |
| Instructions | `.github/instructions/docs.instructions.md`           |
| Agent        | `.github/agents/se-technical-writer.agent.md`         |
| Skill        | `.github/skills/enel-design-system/SKILL.md`          |
| Agent guide  | `AGENTS.md`                                           |

These are adapted from the
[Enel GICT Reference Architectures](https://github.com/ENEL-GICT-PTG/reference_architectures)
repository.

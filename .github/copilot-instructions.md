# EnerGuard Copilot Instructions

You are working in **EnerGuard**, a high-risk AI system under the EU AI Act
(Annex III, critical infrastructure): a predictive-maintenance model for grid
assets with a human-oversight layer. All work must comply with OP35 (Digital
Initiatives Activation), OP36 (Solutions Development & Release Management)
and the [Enel OSPO](https://github.com/ENEL-GICT-PTG/OSPO) guidelines.

## Organizational Compliance Requirements (OP36 design by default)

1. **Cyber Security by Design** (4.6) — never commit secrets; validate external input; OWASP Top 10.
2. **Digital Accessibility (WCAG 2.1 AA)** (4.7) — the dashboard and the docs site must be accessible.
3. **Personal Data Protection by Design** (4.8) — the dataset is synthetic; flag any change that introduces
   personal data (operator IDs in the audit trail are pseudonymous).
4. **Adoption by Design** (4.9) — oversight KPIs A1–A6 measure real use of the supervision layer.
5. **Quality Management** (4.11) — automated quality gates in CI.
6. **Data Security in Non-Production** (4.12) — never use production data without masking.
7. **Intellectual Property by Design** (4.15) — verify licenses of all new dependencies.

## AI Act Invariants (do not break)

- **Single execution point:** only `OversightManager._esegui` executes actions. A decision that is pending,
  rejected, under emergency stop, or HIC auto-executed must never reach it.
- **Routing matrix:** `route()` and `livello_dichiarato()` implement the same matrix as
  `docs/compliance/oversight-declaration.md` (KPI A6 = 100%).
- **Audit trail:** every state transition is logged through `AuditLogger.log`; never write the JSONL by hand.
- **Mandatory justification:** human reviews, stops and resubmissions require ≥ 15 characters.
- **LLM explanations:** the LLM never decides or computes. Keep guardrails and template fallback.

## Coding Standards

- Existing code identifiers and comments are in Italian (hackathon constraint): keep that style in
  existing modules. Documentation in `docs/` and commit messages are in English.
- Follow PEP 8.
- All configuration goes in `.env`; list every variable in `.env.example`.
- Commit messages follow Conventional Commits: `type(scope): description`.
- Every design decision gets a `D-NN` entry in `TRACCIAMENTO_MODIFICHE.md` and a `DECISIONE:` comment.
- New source files start with `# SPDX-License-Identifier: Apache-2.0`.

## Documentation

- Site built with Zensical (`zensical.toml`); new pages must be added to `nav`.
- Theme follows the Enel Design System (`--enel-*` tokens, Inter font, magenta primary, ocean blue accent);
  see `.github/skills/enel-design-system/SKILL.md`.

## Security Guardrails

- Never expose API keys, tokens, or passwords in code, logs or prompts.
- Treat dataset fields sent to the LLM as untrusted input (prompt injection).
- Pin GitHub Actions to commit SHAs.

## Summary

<!-- What does this PR change and why? -->

## Type of change

- [ ] `feat` — new feature
- [ ] `fix` — bug fix
- [ ] `docs` — documentation only
- [ ] `refactor` / `chore` / `ci`

## Decision log

- [ ] No design decision involved
- [ ] New or updated decision `D-__` in `TRACCIAMENTO_MODIFICHE.md` and `DECISIONE:` comment in code

## Oversight checklist (AI Act Art. 12–14)

- [ ] Every action still goes through `OversightManager._esegui` only
- [ ] `route()` and `livello_dichiarato()` match `docs/compliance/oversight-declaration.md`
- [ ] Every new state transition is logged through `AuditLogger`
- [ ] Emergency stop still blocks the existing queue and new decisions

## OP36 checklist

- [ ] No secrets or credentials committed; `.env.example` updated if needed
- [ ] New dependencies have compatible licenses (no AGPL/SSPL/GPL-3.0)
- [ ] User-facing changes respect WCAG 2.1 AA
- [ ] Docs updated (`docs/` and `zensical.toml` nav)

## How was this tested?

<!-- Commands run, dashboard tests T1–T6 exercised, screenshots -->

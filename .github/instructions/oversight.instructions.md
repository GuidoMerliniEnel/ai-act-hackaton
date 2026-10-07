---
applyTo: "oversight_manager.py,app.py,audit_logger.py,bias_detector.py"
---

# Human Oversight Invariants (AI Act Art. 12–14)

- `OversightManager._esegui` is the only execution point. Never call an action elsewhere.
- Never auto-execute HIC decisions; HOTL only for light actions, low risk, high confidence, no active alert.
- If you change `route()`, apply the same change to `livello_dichiarato()` and to
  `docs/compliance/oversight-declaration.md` (KPI A6 must stay 100%).
- Every state change calls `self.audit.log(...)` with actor, event and decision.
- Emergency stop must block both new decisions and the existing queue; deactivation needs a second operator.
- Human justifications: minimum 15 characters, duplicates rejected.
- Record new design choices as `D-NN` in `TRACCIAMENTO_MODIFICHE.md` with a `DECISIONE:` comment.

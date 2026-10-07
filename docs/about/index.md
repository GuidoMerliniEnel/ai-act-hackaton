# About

## Scenario

An energy distribution company uses machine learning to decide which grid
assets to inspect or maintain before they fail. A missed failure on a
hospital feeder is irreversible; an unnecessary inspection only costs time.
The model is useful, but it **must not act alone**.

The EU AI Act classifies AI systems used as safety components in the
management of critical infrastructure, including electricity grids, as
**high risk** (Annex III, point 2). These systems must be designed for
effective human oversight (Art. 14) and carry the full set of high-risk
obligations from 2 August 2026.

## The Hackathon

EnerGuard was built during the **AI Human Oversight Hackathon**
(Deloitte × Enel FNC, 7 October 2026), in four tiers:

| Tier | Goal                                          | Deliverable                                                  |
| ---- | --------------------------------------------- | ------------------------------------------------------------ |
| 1    | Model and data: find the hidden bias          | `predizioni.csv`, disaggregated metrics, anomalies observed  |
| 2    | Human oversight: routing, queue, stop         | Working approve/modify/reject flow and emergency stop        |
| 3    | Explainability, bias and drift monitoring     | Complete dashboard and at least one automatic alert          |
| 4    | Presentation                                  | Model card, impact assessment, oversight declaration, demo   |

The jury does not reward AUC. It rewards an oversight layer that really
blocks, really requires a justification, and really stops. This is checked
live with the six [verification tests](../quality/verification-tests.md).

## Governance

The repository follows:

- **[Enel OSPO](https://github.com/ENEL-GICT-PTG/OSPO)** guidelines:
  required files, SPDX headers, Conventional Commits, CI quality gates,
  documentation with Zensical.
- **OP35 / OP36** design-by-default requirements, as encoded in the
  [Enel GICT Reference Architectures](https://github.com/ENEL-GICT-PTG/reference_architectures):
  cyber security, accessibility, privacy, adoption, quality and
  intellectual property.

| OP36 requirement                       | How EnerGuard addresses it                                                    |
| -------------------------------------- | ----------------------------------------------------------------------------- |
| 4.6 Cyber Security by Design           | Secrets only in `.env`; pinned Actions; `pip-audit`; LLM output guardrails   |
| 4.7 Digital Accessibility (WCAG 2.1 AA) | Docs theme with AA contrast; text-based status in the dashboard, not color only |
| 4.8 Personal Data Protection           | Synthetic dataset; operator IDs are pseudonymous                               |
| 4.9 Adoption by Design                 | KPIs A1–A6 measure real use of the supervision layer                           |
| 4.11 Quality Management                | CI: build, smoke tests, docs build, security and license gates               |
| 4.12 Data Security in Non-Production   | No production data is used                                                     |
| 4.15 Intellectual Property by Design   | Apache-2.0, `NOTICE`, license gate blocking AGPL/SSPL/GPL-3.0                  |

## Language

Source code, code comments and the decision log
(`TRACCIAMENTO_MODIFICHE.md`) are in Italian, as required by the
hackathon. This documentation is in English.

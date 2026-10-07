# Compliance

## AI Act classification

| Item            | Assessment                                                                                                                                                                   |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| System          | Predictive maintenance recommendations for electricity grid assets                                                                                                           |
| Classification  | **High risk** — Annex III, point 2: AI systems intended as safety components in the management and operation of critical infrastructure, including the supply of electricity |
| Rationale       | Recommendations influence whether a failure on a feeder serving hospitals or other critical users is prevented. A missed failure can interrupt an essential service          |
| Applicable from | 2 August 2026                                                                                                                                                                |
| Not prohibited  | No Art. 5 practice; no biometric or personal data processing                                                                                                                 |

## Requirements mapping

| Article | Requirement                         | Where it is addressed                                                         |
| ------- | ----------------------------------- | ----------------------------------------------------------------------------- |
| Art. 9  | Risk management system              | [Impact assessment](impact-assessment.md), [decisions](../decisions/index.md) |
| Art. 10 | Data and data governance, bias      | [Dataset](../architecture/dataset.md), Tier 1 investigation, `BiasDetector`   |
| Art. 11 | Technical documentation             | This site, [model card](model-card.md)                                        |
| Art. 12 | Record-keeping                      | `AuditLogger`: hash-chained log of every transition                           |
| Art. 13 | Transparency to the deployer        | [Model card](model-card.md), explanations with declared source                |
| Art. 14 | Human oversight                     | [Oversight declaration](oversight-declaration.md), dashboard, emergency stop  |
| Art. 15 | Accuracy, robustness, cybersecurity | Disaggregated metrics, drift alert, LLM fallback, CI security gate            |

### Art. 14(4) capabilities

| Capability                                          | Dashboard element                                                         | Test / KPI |
| --------------------------------------------------- | ------------------------------------------------------------------------- | ---------- |
| (a) Understand capacities and limits, monitor       | Model card, Bias & drift tab, KPI tab                                     | C1–C4      |
| (b) Remain aware of automation bias                 | Mandatory justification, rubber-stamping index, uncertainty on every card | A3, A4, B2 |
| (c) Correctly interpret the output                  | Plain-language explanation with three factors and direction               | B1, T4     |
| (d) Decide not to use, disregard, override, reverse | Reject / Modify with justification                                        | A2, T1, T2 |
| (e) Intervene or interrupt (stop button)            | Emergency stop: global or partial, one click plus confirmation            | B4, T3     |

## Provider and deployer

In a real deployment:

| Role         | Who                                                                                                                                                                    | Main obligations                                                                                                                                                                                                                                                                                                                                                                                                      |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Provider** | The organisation that develops EnerGuard and places it on the market or puts it into service under its name (e.g. Enel's internal digital unit, or an external vendor) | Risk management (Art. 9), data governance (Art. 10), technical documentation (Art. 11), logging capability (Art. 12), instructions for use (Art. 13), oversight by design (Art. 14), accuracy and robustness (Art. 15), quality management system (Art. 17), conformity assessment, CE marking and EU database registration (Art. 43, 48, 49), post-market monitoring (Art. 72), serious incident reporting (Art. 73) |
| **Deployer** | The grid operator using the system in its control rooms (e.g. the distribution company)                                                                                | Use according to instructions (Art. 26(1)), assign competent and trained human overseers (Art. 26(2)), ensure input data relevance (Art. 26(4)), monitor operation and report risks (Art. 26(5)), keep logs for at least six months (Art. 26(6)), inform workers' representatives (Art. 26(7)), fundamental rights impact assessment where applicable (Art. 27)                                                       |

<!-- prettier-ignore-start -->
!!! note "Same group, two roles"

    If Enel develops the system internally and uses it in its own grid
    operations, the same group holds both roles and both sets of
    obligations apply.
<!-- prettier-ignore-end -->

## Deliverables

The official deliverables are the Italian documents in `consegna/`
(model card, impact assessment, oversight declaration, demo script and test
answers). The pages below are their English summaries.

- [Model card](model-card.md)
- [Impact assessment](impact-assessment.md)
- [Oversight declaration](oversight-declaration.md)

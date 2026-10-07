# EnerGuard — Human Oversight for Predictive Maintenance

[![CI](https://github.com/GuidoMerliniEnel/ai-act-hackaton/actions/workflows/ci.yml/badge.svg)](https://github.com/GuidoMerliniEnel/ai-act-hackaton/actions/workflows/ci.yml)
[![Documentation](https://github.com/GuidoMerliniEnel/ai-act-hackaton/actions/workflows/docs.yml/badge.svg)](https://github.com/GuidoMerliniEnel/ai-act-hackaton/actions/workflows/docs.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

A predictive-maintenance model for grid assets wrapped in an **EU AI Act
Art. 14 human-oversight layer**. Recommendations are routed by risk to
HIC / HITL / HOTL and land in an approval queue with mandatory
justifications. The layer adds an emergency stop and bias and drift
monitoring. Cards carry plain-language explanations with a "what if"
scenario, and every step goes to a tamper-evident audit trail.

Built during the *AI Human Oversight Hackathon* (Deloitte × Enel FNC,
7 October 2026) on top of the EnerGuard starter kit. The system is
**high risk** under the AI Act (Annex III, point 2: critical
infrastructure, electricity supply).

> Code, comments, the decision log and the submission documents are in
> Italian, as required by the hackathon. The documentation site in
> [`docs/`](docs/index.md) is in English, following the Enel OSPO guidelines.

## Quick Start

```bash
./run_dashboard.sh              # macOS / Linux
run_dashboard.bat               # Windows
```

The script creates `.venv` and installs `requirements.txt`. On the first
run, or with `--retrain`, it also trains the model. It then opens the
dashboard at <http://localhost:8501>.

| Option                                 | Effect                                            |
| -------------------------------------- | ------------------------------------------------- |
| `--retrain`                            | Retrain the model even if `modello.joblib` exists |
| `--port N`                             | Serve on port `N` (`.sh` only, default 8501)      |
| `PYTHON=python3.12 ./run_dashboard.sh` | Use a specific interpreter                        |

Stop with `Ctrl+C`. The queue lives in memory and
resets on restart; only `audit_trail.jsonl` persists.

### Manual steps

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python train_baseline.py        # modello.joblib + predizioni.csv, prints fairness report
streamlit run app.py            # dashboard
python prova_test_giuria.py     # rehearsal of the 6 jury tests (expect 8/8)
python test_llm.py              # explanation engine: template and LLM
```

## What Was Built

### Tier 1 — Model and data (D-01..D-07)

- Random forest (300 trees, balanced classes). **AUC 0.868, recall 0.837**
  on 720 test assets.
- Thresholds per user criticality: **0.30** for standard users, **0.20**
  for high and critical users, under a declared 10:1 cost of a missed
  failure vs an unnecessary inspection.
- **Hidden bias found:** South and Islands have almost identical profiles,
  but recorded failure rates are 0.24 vs 0.45. Hypothesis: failures are
  under-reported in the South, the only badly calibrated area (gap 0.177).
- **Mitigations, measured before and after:**
  - `area_geografica` removed from the model: recall gap between areas
    0.41 → 0.22.
  - Thresholds per criticality: missed failures on critical/high users
    3/6 → 1/1.
  - Calibration alert that promotes the South to HITL.

### Tier 2 — Human oversight (D-08..D-18)

- **Routing matrix** in `route()`, plus an independent copy in
  `livello_dichiarato()`; KPI A6 checks they agree.
  - HIC: critical users, or load reduction on high users.
  - HITL: p ≥ 0.60, confidence < 0.80, an alerted area, or a non-light
    action.
  - HOTL: low-risk routine only.
- **Single execution point** `_esegui`. It rejects pending, rejected,
  stopped and HIC auto-executed decisions.
- **Mandatory justification** of at least 15 characters, with copy-paste
  blocked. 30-minute **SLA** with escalation.
- **Emergency stop:**
  - Scope is global, per area, per asset type, or combined (e.g.
    `area:Sud+tipo:linea_AT`). It also freezes the existing queue.
  - Activation is one click plus confirmation.
  - Deactivation needs a second operator (four eyes).
  - Blocked decisions return only through an explicit resubmission.
- **KPIs A1–A6** in the dashboard.

### Tier 3 — Explainability, bias, monitoring (D-19..D-30)

- **Explanations:** top three SHAP factors, led by the risk-increasing
  ones. Each value is judged against fleet percentiles. Text comes from an
  LLM (Azure) with guardrails and a template fallback, and its source is
  declared and logged.
- **Calibration alert** > 0.10 promotes the area to HITL. **Drift alert**:
  two consecutive simulated weeks below reference − 0.10 disables HOTL
  everywhere.
- **Override rate per area**, with an alert above twice the average.
- **Confidence × risk matrix**, colored by the declared level.
- **Audit tab:** reconstruct a decision by asset ID; filter by asset,
  actor and period; export CSV/JSONL. Hash-chain integrity is always shown
  in the sidebar.

### Tier 4 — Understandability and delivery (D-31..D-35)

- **"In parole semplici" box** on every card: traffic light, "about N in
  10" probability, what to do, warnings. It is built from fixed rules, not
  the LLM.
- **"What if" scenario:** the model re-predicts with the main factor set
  back to the fleet median and says whether the intervention would still
  be needed. This is a contrastive explanation.
- **`prova_test_giuria.py`:** repeatable rehearsal of tests T1–T6 on
  temporary logs. Result: 8/8.
- **Submission documents** in [`consegna/`](consegna/):

| Document | Content |
| --- | --- |
| [1_Model_Card.md](consegna/1_Model_Card.md) | Purpose, data, global and subgroup metrics, confidence, limits, AI Act classification |
| [2_Relazione_Impatto.md](consegna/2_Relazione_Impatto.md) | Risks, mitigations, what is not solved |
| [3_Dichiarazione_Oversight.md](consegna/3_Dichiarazione_Oversight.md) | Routing matrix with justifications |
| [4_Scaletta_Demo_e_Test.md](consegna/4_Scaletta_Demo_e_Test.md) | 5–7 min demo script and answers to tests T1–T6 |

Every decision (D-01..D-37) is recorded with its rationale in
[TRACCIAMENTO_MODIFICHE.md](TRACCIAMENTO_MODIFICHE.md) and cited in the
code as `DECISIONE:` comments.

## Dashboard

| Area           | Content                                                                                         |
| -------------- | ----------------------------------------------------------------------------------------------- |
| Sidebar        | Operator ID, explanation engine, **emergency stop**, active stops, audit-chain integrity        |
| Coda decisioni | Cards with plain-language box, explanation, three factors, approve / modify / reject / escalate |
| Matrice        | Confidence × risk, colored by declared level, dashed thresholds                                 |
| Bias & drift   | Disaggregated metrics, calibration per area, weekly drift, override per area                    |
| Audit trail    | Reconstruction by asset, filters, CSV/JSONL export                                              |
| KPI            | A1–A6 with targets, level distribution                                                          |

## Configuration (optional LLM)

Without `.env` the dashboard uses deterministic templates. To enable LLM
explanations:

```bash
cp .env.example .env    # set LLM_PROVIDER, LLM_API_KEY, LLM_MODEL, LLM_BASE_URL
python test_llm.py      # shows factors, template and LLM text, source and latency
```

Step-by-step guide: [GUIDA_LLM_Configurazione.md](GUIDA_LLM_Configurazione.md).
`.env` is git-ignored and must never be committed or submitted.

**Guarantees:**

- The LLM never decides or computes.
- Its output is discarded if it cites numbers not present in the data,
  uses jargon, or omits the main factor.
- It falls back automatically to the template on any error.
- Every explanation declares its source (`template`, `llm:…`,
  `template(fallback:…)`).

## Dataset

`energuard_dataset.csv`: 2,400 synthetic assets, comma separator.
`energuard_dataset_EXCEL.csv` has the same table with `;` and decimal `,`
for Italian Excel. `energuard_dataset.xlsx` includes a column dictionary.
`utils_io.carica_csv()` reads both CSV formats.

## Documentation Site (Zensical)

The documentation in `docs/` is built with [Zensical](https://zensical.org/),
a static site generator from the creators of Material for MkDocs. The
configuration and theme follow the
[Enel OSPO](https://github.com/ENEL-GICT-PTG/OSPO) site (Enel Design System:
magenta primary, ocean blue accent, Inter font, light and dark mode).

```bash
pip install -r requirements-docs.txt   # pinned zensical version
zensical serve                         # http://localhost:8000, reloads on save (-o opens the browser)
zensical build --clean                 # static HTML in site/ (--clean drops the cache)
```

To add a page, create the Markdown file under `docs/` and register it in
the `nav` list of `zensical.toml`: pages missing from `nav` are **silently
dropped**. Enabled extensions: admonitions, tabs, task lists, footnotes,
tables, emoji, code copy, Mermaid. Theme colors come only from the
`--enel-*` tokens in `docs/stylesheets/extra.css` (see
`.github/skills/enel-design-system/SKILL.md`).

`.github/workflows/docs.yml` deploys the site to GitHub Pages on every push
to `main`. One-time setup: **Settings → Pages → Source: GitHub Actions**.

## Project Structure

```text
├── .github/                    # CI/CD, issue/PR templates, Copilot customizations
├── docs/                       # documentation site source (English)
├── overrides/                  # Zensical template overrides
├── run_dashboard.sh / .bat     # one-command launcher
├── app.py                      # Streamlit supervision dashboard
├── oversight_manager.py        # routing, queue, SLA, emergency stop, KPIs
├── bias_detector.py            # disaggregated metrics, calibration, drift
├── explainer.py                # SHAP, template/LLM text, plain-language box, "what if"
├── audit_logger.py             # hash-chained JSONL audit trail
├── train_baseline.py           # model training and fairness report
├── utils_io.py                 # CSV loading, feature preparation, thresholds
├── prova_test_giuria.py        # rehearsal of jury tests T1–T6
├── test_llm.py                 # explanation engine smoke test
├── consegna/                   # Tier 4 submission documents
├── TRACCIAMENTO_MODIFICHE.md   # decision log D-01..D-37
├── zensical.toml               # documentation site configuration
├── requirements.txt            # application dependencies
├── requirements-docs.txt       # documentation dependencies
└── energuard_dataset*.csv      # synthetic dataset
```

## Known Limits

Detailed in the model card and impact report. In brief:

- The recall gap in the North (0.216) remains: those failures show no
  sensor signal.
- The South label bias is managed by oversight, not removed.
- Confidence `max(p, 1-p)` adds little beyond the probability.
- Drift is simulated, because the dataset has no dates.
- Operator identity is self-declared.
- State is held in memory.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All participants are expected to
follow the [Code of Conduct](CODE_OF_CONDUCT.md). Report vulnerabilities as
described in [SECURITY.md](SECURITY.md).

## License

Licensed under the [Apache License 2.0](LICENSE). See [NOTICE](NOTICE) for
attributions.

## Acknowledgements

- Deloitte × Enel FNC — EnerGuard starter kit and hackathon materials
- [Enel OSPO](https://github.com/ENEL-GICT-PTG/OSPO) — repository and
  documentation guidelines
- [Enel GICT Reference Architectures](https://github.com/ENEL-GICT-PTG/reference_architectures)
  — OP35/OP36 governance and Copilot customizations
- [scikit-learn](https://scikit-learn.org/), [SHAP](https://shap.readthedocs.io/),
  [Streamlit](https://streamlit.io/), [Zensical](https://zensical.org/)

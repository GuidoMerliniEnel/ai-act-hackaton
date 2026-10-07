# Installation

## Prerequisites

- Python 3.11 or later (the hackathon kit uses 3.11; pinned versions install on 3.11 to 3.14)
- Git

## Set up the environment

```bash
git clone https://github.com/GuidoMerliniEnel/ai-act-hackaton.git
cd ai-act-hackaton

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Train the model

```bash
python train_baseline.py
```

The script:

- trains a random forest on 70% of the dataset;
- applies the decision thresholds per user criticality
  ([D-01](../decisions/index.md#d-01), [D-02](../decisions/index.md#d-02));
- prints AUC, the classification report and disaggregated metrics by area,
  asset type and user criticality, with fairness alerts;
- writes `modello.joblib` and `predizioni.csv` (test set, 720 assets).

Expected output: AUC ≈ 0.868.

## Run the dashboard

```bash
streamlit run app.py
```

Open <http://localhost:8501>. The first load takes a few seconds while
explanations for the visible cards are generated.

## Build the documentation

```bash
pip install -r requirements-docs.txt
zensical serve            # live preview at http://localhost:8000
zensical build --clean    # static HTML in site/
```

!!! note "Generated files"
    `modello.joblib`, `predizioni.csv`, `audit_trail.jsonl`, `.env` and
    `site/` are git-ignored.

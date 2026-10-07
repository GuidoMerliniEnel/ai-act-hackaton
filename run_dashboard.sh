#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Avvia la dashboard EnerGuard: crea il venv, installa le dipendenze, addestra il modello se serve.
# Uso: ./run_dashboard.sh [--retrain] [--port N]
set -euo pipefail
cd "$(dirname "$0")"

PORT=8501
RETRAIN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --retrain) RETRAIN=1; shift ;;
    --port) PORT="$2"; shift 2 ;;
    -h|--help) sed -n '3,4p' "$0"; exit 0 ;;
    *) echo "Opzione sconosciuta: $1" >&2; exit 2 ;;
  esac
done

PYTHON="${PYTHON:-python3}"
if [[ ! -d .venv ]]; then
  echo ">> Creo l'ambiente virtuale .venv"
  "$PYTHON" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

if [[ ! -f .venv/.deps-ok || requirements.txt -nt .venv/.deps-ok ]]; then
  echo ">> Installo le dipendenze"
  pip install -q --upgrade pip
  pip install -q -r requirements.txt
  touch .venv/.deps-ok
fi

if [[ $RETRAIN -eq 1 || ! -f modello.joblib || ! -f predizioni.csv ]]; then
  echo ">> Addestro il modello (train_baseline.py)"
  python train_baseline.py
fi

[[ -f .env ]] || echo ">> Nessun .env: spiegazioni a template (vedi .env.example per l'LLM)"

echo ">> Dashboard su http://localhost:${PORT} (Ctrl+C per fermare)"
exec streamlit run app.py --server.port "$PORT" --server.headless true

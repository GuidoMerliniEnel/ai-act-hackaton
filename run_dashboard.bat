@echo off
REM SPDX-License-Identifier: Apache-2.0
REM Avvia la dashboard EnerGuard su Windows. Uso: run_dashboard.bat [--retrain]
setlocal
cd /d "%~dp0"

if not exist .venv (
  echo ^>^> Creo l'ambiente virtuale .venv
  python -m venv .venv || exit /b 1
)
call .venv\Scripts\activate.bat

if not exist .venv\.deps-ok (
  echo ^>^> Installo le dipendenze
  python -m pip install -q --upgrade pip
  pip install -q -r requirements.txt || exit /b 1
  type nul > .venv\.deps-ok
)

set RETRAIN=0
if "%~1"=="--retrain" set RETRAIN=1
if not exist modello.joblib set RETRAIN=1
if not exist predizioni.csv set RETRAIN=1
if "%RETRAIN%"=="1" (
  echo ^>^> Addestro il modello
  python train_baseline.py || exit /b 1
)

if not exist .env echo ^>^> Nessun .env: spiegazioni a template

echo ^>^> Dashboard su http://localhost:8501 (Ctrl+C per fermare)
streamlit run app.py --server.port 8501 --server.headless true

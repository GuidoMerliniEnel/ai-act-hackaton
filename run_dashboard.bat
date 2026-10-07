@echo off
REM SPDX-License-Identifier: Apache-2.0
REM Avvia la dashboard EnerGuard su Windows. Uso: run_dashboard.bat [--retrain]
setlocal
cd /d "%~dp0"

REM D-38: con Python < 3.12 le versioni fissate non si installano e i numeri cambierebbero
python -c "import sys; sys.exit(sys.version_info < (3, 12))" || (
  echo Serve Python 3.12 o superiore. Installalo da python.org e rilancia.
  exit /b 1
)
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe -c "import sys; sys.exit(sys.version_info < (3, 12))" || (
    echo .venv usa Python ^< 3.12: cancella la cartella .venv e rilancia lo script.
    exit /b 1
  )
)

if not exist .venv (
  echo ^>^> Creo l'ambiente virtuale .venv
  python -m venv .venv || exit /b 1
)
call .venv\Scripts\activate.bat

set RETRAIN=0
REM .deps-ok e' una copia di requirements.txt: se differisce si reinstalla e si riaddestra
fc /b requirements.txt .venv\.deps-ok >nul 2>&1 || (
  echo ^>^> Installo le dipendenze
  python -m pip install -q --upgrade pip
  pip install -q -r requirements.txt || exit /b 1
  copy /y requirements.txt .venv\.deps-ok >nul
  set RETRAIN=1
)

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

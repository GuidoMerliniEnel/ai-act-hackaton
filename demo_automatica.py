# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Enel SpA
"""
EnerGuard - demo automatica narrata
===================================
Legge il discorso (consegna/5_Discorso_Presentazione.md), lo pronuncia con una voce
sintetica e intanto guida la dashboard con Playwright, seguendo le istruzioni tra
parentesi quadre del discorso.

Prerequisiti:  pip install -r requirements-demo.txt && python -m playwright install chromium
Esecuzione:    ./run_dashboard.sh            (terminale 1)
               python demo_automatica.py     (terminale 2)
Opzioni:       --voce say|edge|nessuna  --velocita 185  --registra cartella_video  --headless

Attenzione: la demo rifiuta davvero AST-01148 e attiva uno stop. Riavviare la dashboard
per ripartire da una coda pulita.
"""

import argparse
import asyncio
import platform
import re
import subprocess
import tempfile
import threading
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

DISCORSO = Path(__file__).parent / "consegna" / "5_Discorso_Presentazione.md"
CARD = "AST-01148"
MOTIVAZIONE_VERA = "Sopralluogo di ieri: vibrazione nella norma, sensore da ricalibrare"
AMBITO_STOP = "area:Sud+tipo:linea_AT"
MOTIVAZIONE_STOP = "Letture anomale dai sensori delle linee AT del Sud"


# ---------------------------------------------------------------------------
# Discorso: blocchi (azione, testo da pronunciare)
# ---------------------------------------------------------------------------
def pulisci(testo: str) -> str:
    testo = re.sub(r"[*`_]", "", testo)
    testo = testo.replace("0.", "zero virgola ").replace("→", "a")
    return re.sub(r"\s+", " ", testo).strip()


def leggi_discorso(percorso: Path) -> list[tuple[str, str, str]]:
    """Ritorna (titolo sezione, istruzione tra parentesi quadre, testo) in ordine."""
    blocchi, titolo, azione, righe = [], "", "", []

    def chiudi():
        if righe or azione:
            blocchi.append((titolo, azione, pulisci(" ".join(righe))))

    for riga in percorso.read_text(encoding="utf-8").splitlines():
        if riga.startswith("## Copertura") or riga.startswith("## Promemoria"):
            break
        if riga.startswith("#"):
            chiudi()
            titolo, azione, righe = riga.lstrip("# ").strip(), "", []
        elif riga.startswith("["):
            chiudi()
            azione, righe = riga.strip("[] "), []
        elif riga.startswith(">"):
            righe.append(riga.lstrip("> ").lstrip("- "))
    chiudi()
    return [b for b in blocchi if b[1] or b[2]]


# ---------------------------------------------------------------------------
# Voce
# ---------------------------------------------------------------------------
def parla(testo: str, voce: str, velocita: int):
    if not testo or voce == "nessuna":
        return
    if voce == "say":
        subprocess.run(["say", "-v", "Alice", "-r", str(velocita), testo], check=False)
        return
    import edge_tts  # voce neurale, richiede rete

    mp3 = Path(tempfile.mkdtemp()) / "voce.mp3"
    asyncio.run(edge_tts.Communicate(testo, "it-IT-ElsaNeural").save(str(mp3)))
    if platform.system() == "Darwin":
        subprocess.run(["afplay", str(mp3)], check=False)
    else:
        subprocess.run(["powershell", "-c",
                        "Add-Type -AssemblyName presentationCore; $p=New-Object System.Windows.Media.MediaPlayer; "
                        f"$p.Open('{mp3}'); $p.Play(); Start-Sleep -s 1; "
                        "while($p.Position -lt $p.NaturalDuration.TimeSpan){Start-Sleep -m 200}"], check=False)


# ---------------------------------------------------------------------------
# Azioni sulla dashboard
# ---------------------------------------------------------------------------
def attendi(page: Page):
    """Aspetta che Streamlit finisca il rerun."""
    page.wait_for_timeout(700)
    try:
        page.locator('[data-testid="stStatusWidget"]').wait_for(state="hidden", timeout=20000)
    except Exception:
        pass
    page.wait_for_timeout(500)


def evidenzia(page: Page, locator):
    locator.scroll_into_view_if_needed()
    locator.evaluate("e => { e.style.outline = '4px solid #d3135a'; e.style.outlineOffset = '4px'; }")


def scheda(page: Page, nome: str):
    page.get_by_role("tab", name=nome).click()
    attendi(page)


def card(page: Page):
    return page.locator('[data-testid="stExpander"]', has_text=CARD).first


def apri_card(page: Page):
    scheda(page, "Coda decisioni")
    c = card(page)
    c.locator("summary").click()
    attendi(page)
    evidenzia(page, c)


def rifiuta(page: Page, motivazione: str):
    c = card(page)
    campo = c.get_by_label("Motivazione (obbligatoria)")
    campo.fill(motivazione)
    campo.press("Tab")
    attendi(page)
    c.get_by_role("button", name="Rifiuta").click()
    attendi(page)


def giro_bias(page: Page):
    for titolo in ("Recall per area", "Gruppi incrociati", "Drift di performance", "Override umano per area"):
        page.get_by_text(titolo, exact=False).first.scroll_into_view_if_needed()
        page.wait_for_timeout(6000)


def audit(page: Page):
    scheda(page, "Audit trail")
    campo = page.get_by_label("Asset contiene")
    campo.fill(CARD)
    campo.press("Enter")
    attendi(page)
    evidenzia(page, page.get_by_text("Ricostruisci una decisione").first)


def stop(page: Page):
    barra = page.locator('[data-testid="stSidebar"]')
    barra.get_by_label("Ambito").click()
    page.get_by_role("option", name=AMBITO_STOP).click()
    attendi(page)
    campo = barra.get_by_label("Motivazione stop (min 15 caratteri)")
    campo.fill(MOTIVAZIONE_STOP)
    campo.press("Enter")
    attendi(page)
    barra.get_by_role("button", name="ATTIVA STOP").click()
    attendi(page)
    barra.get_by_role("button", name="Conferma").click()
    attendi(page)
    page.evaluate("window.scrollTo(0, 0)")


AZIONI = [  # (parola chiave nell'istruzione tra parentesi quadre, funzione)
    ("barra dei KPI", lambda p: evidenzia(p, p.get_by_text("In attesa di revisione").first)),
    ("Aprire la card", apri_card),
    ('Scrivere "ok"', lambda p: rifiuta(p, "ok")),
    ('Scrivere "', lambda p: rifiuta(p, MOTIVAZIONE_VERA)),
    ("Audit trail", audit),
    ("ATTIVA STOP", stop),
    ("Scheda Bias", lambda p: scheda(p, "Bias & drift")),
    ("recall con intervallo", giro_bias),
    ("Matrice", lambda p: scheda(p, "Matrice confidenza × rischio")),
]


def azione_per(istruzione: str):
    return next((f for chiave, f in AZIONI if chiave in istruzione), None)


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Demo narrata della dashboard EnerGuard")
    ap.add_argument("--url", default="http://localhost:8501")
    ap.add_argument("--voce", choices=["say", "edge", "nessuna"],
                    default="say" if platform.system() == "Darwin" else "edge")
    ap.add_argument("--velocita", type=int, default=185, help="parole al minuto (say)")
    ap.add_argument("--registra", help="cartella in cui salvare il video della sessione")
    ap.add_argument("--headless", action="store_true")
    args = ap.parse_args()

    blocchi = leggi_discorso(DISCORSO)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=args.headless, slow_mo=250)
        contesto = browser.new_context(viewport={"width": 1600, "height": 900},
                                       record_video_dir=args.registra)
        page = contesto.new_page()
        page.goto(args.url)
        page.get_by_text("In attesa di revisione").first.wait_for(timeout=60000)
        attendi(page)

        for titolo, istruzione, testo in blocchi:
            print(f"\n== {titolo}" + (f"  [{istruzione}]" if istruzione else ""))
            voce = threading.Thread(target=parla, args=(testo, args.voce, args.velocita))
            voce.start()
            azione = azione_per(istruzione) if istruzione else None
            if azione:
                try:
                    azione(page)
                except Exception as e:  # la demo continua anche se un passo non riesce
                    print(f"   azione non riuscita: {e.__class__.__name__}: {str(e)[:120]}")
            voce.join()

        page.wait_for_timeout(2000)
        contesto.close()
        browser.close()
    if args.registra:
        print(f"\nVideo salvato in {args.registra}")


if __name__ == "__main__":
    main()

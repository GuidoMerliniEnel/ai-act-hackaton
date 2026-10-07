"""
EnerGuard - prova generale dei 6 test della giuria (documento "Indicatori di qualita'", Strato 2)
================================================================================================
Esecuzione: python prova_test_giuria.py
Usa solo log temporanei: non tocca audit_trail.jsonl ne' .env. Esce con codice 1 se un test fallisce.
"""
import json
import os
import shutil
import tempfile
import warnings

import joblib

from audit_logger import AuditLogger
from bias_detector import BiasDetector
from explainer import ConfigLLM, SpiegatoreLLM, estrai_fattori
from oversight_manager import OversightManager, Raccomandazione, StatoDecisione as S
from utils_io import carica_csv, prepara_feature

warnings.filterwarnings("ignore")
esiti = []


def verifica(test: str, condizione: bool, dettaglio: str):
    esiti.append((test, condizione))
    print(f"  [{'OK' if condizione else 'FALLITO'}] {test}: {dettaglio}")


def nuovo_sistema():
    log = AuditLogger(os.path.join(tempfile.mkdtemp(), "audit.jsonl"))
    om = OversightManager(log)
    eseguite = []
    originale = om._esegui
    om._esegui = lambda r: (eseguite.append(r.id), originale(r))[1]
    return om, log, eseguite


def rac(asset, tipo, area, crit="standard", p=0.7, c=0.7, azione="programma_manutenzione"):
    return Raccomandazione(asset, tipo, area, crit, p, c, azione, [])


print("\nT1 · Override reale (cancello)")
om, log, eseguite = nuovo_sistema()
r = om.sottometti(rac("AST-T1", "trasformatore", "Nord"))
om.revisiona(r.id, S.RIFIUTATA, "OP-001", "Ispezione eseguita ieri, nessuna anomalia riscontrata")
verifica("T1", r.stato == S.RIFIUTATA and r.id not in eseguite,
         f"decisione {r.livello.value} rifiutata, stato {r.stato.value}, esecuzioni: {len(eseguite)}")
chiamate = [l.strip() for l in open("oversight_manager.py", encoding="utf-8") if "self._esegui(" in l]
print(f"         punti che chiamano _esegui: {len(chiamate)} (HOTL auto-eseguita e revisione APPROVATA/MODIFICATA)")

print("\nT2 · Motivazione (cancello)")
om, log, _ = nuovo_sistema()
r1 = om.sottometti(rac("AST-T2a", "linea_AT", "Centro"))
r2 = om.sottometti(rac("AST-T2b", "linea_AT", "Centro"))
respinte = []
for m in ("", "ok"):
    try:
        om.revisiona(r1.id, S.APPROVATA, "OP-001", m)
    except ValueError:
        respinte.append(repr(m))
testo = "Vibrazione confermata dal sopralluogo di stamattina"
om.revisiona(r1.id, S.APPROVATA, "OP-001", testo)
try:
    om.revisiona(r2.id, S.APPROVATA, "OP-001", testo.upper())
    fotocopia = False
except ValueError:
    fotocopia = True
verifica("T2", len(respinte) == 2 and fotocopia,
         f"respinte {', '.join(respinte)}; fotocopia respinta: {fotocopia}; A4 = {om.kpi()['A4_indice_rubber_stamping']}")

print("\nT3 · Emergency stop parziale (cancello)")
om, log, eseguite = nuovo_sistema()
dentro = om.sottometti(rac("AST-T3a", "linea_AT", "Sud"))
fuori_area = om.sottometti(rac("AST-T3b", "linea_AT", "Nord"))
fuori_tipo = om.sottometti(rac("AST-T3c", "trasformatore", "Sud"))
bloccate = om.attiva_stop("area:Sud+tipo:linea_AT", "OP-001", "Letture anomale dai sensori delle linee AT del Sud")
nuova = om.sottometti(rac("AST-T3d", "linea_AT", "Sud"))
try:
    om.revisiona(dentro.id, S.APPROVATA, "OP-001", "Tentativo di approvare sotto stop attivo")
    aggirato = True
except ValueError:
    aggirato = False
eventi = [json.loads(l)["evento"] for l in log.path.read_text(encoding="utf-8").splitlines()]
verifica("T3", dentro.stato == S.BLOCCATA_STOP and nuova.stato == S.BLOCCATA_STOP
         and fuori_area.stato == S.IN_ATTESA and fuori_tipo.stato == S.IN_ATTESA
         and not aggirato and "emergency_stop_ON:area:Sud+tipo:linea_AT" in eventi,
         f"bloccate in coda {len(bloccate)}, nuova nell'ambito {nuova.stato.value}, "
         f"Nord e trasformatore Sud ancora IN_ATTESA, approvazione sotto stop respinta, stop nel log")

print("\nT4 · Comprensibilita' e tenuta della spiegazione")
modello = joblib.load("modello.joblib")
df = carica_csv("energuard_dataset.csv")
X = prepara_feature(df)
pred = carica_csv("predizioni.csv")
riga = pred[pred["y_pred"] == 1].iloc[0]
fattori = estrai_fattori(modello, X.loc[df["asset_id"] == riga["asset_id"]].iloc[0], list(X.columns))
rec = {"asset_id": riga["asset_id"], "tipo_asset": riga["tipo_asset"], "area_geografica": riga["area_geografica"],
       "criticita_utenza": riga["criticita_utenza"], "prob_guasto": float(riga["proba"]),
       "confidenza": float(riga["confidenza"]), "azione_proposta": "programma_manutenzione",
       "livello": "HITL", "soglia_confidenza": 0.80}
for scenario, modifica in (("chiave errata", {"api_key": "chiave-volutamente-errata"}),
                           ("rete staccata", {"base_url": "https://127.0.0.1:9", "timeout": 2})):
    cfg = ConfigLLM()
    cfg.provider = cfg.provider if cfg.attivo else "azure"
    cfg.model = cfg.model or "modello-di-prova"
    cfg.base_url = cfg.base_url or "https://127.0.0.1:9"
    cfg.api_key = cfg.api_key or "chiave-di-prova"
    for k, v in modifica.items():
        setattr(cfg, k, v)
    sp = SpiegatoreLLM(cfg, usa_cache=False).spiega(rec, fattori)
    verifica(f"T4 {scenario}", sp.fonte.startswith("template(fallback") and len(sp.testo) > 50,
             f"fonte: {sp.fonte[:60]}...; spiegazione presente ({len(sp.testo)} caratteri)")
try:
    SpiegatoreLLM._guardrail({"spiegazione": f"La {fattori[0].etichetta} e' a 99.9, molto alta.",
                              "incertezza": "Confidenza buona."}, fattori, rec)
    guardrail = False
except ValueError as e:
    guardrail = "non presente" in str(e)
verifica("T4 guardrail", guardrail, "una risposta con un numero inventato (99.9) viene scartata")

print("\nT5 · Bias nascosto")
bd = BiasDetector()
cal = bd.calibrazione_per_gruppo(pred, "area_geografica").set_index("area_geografica")
prof = df.groupby("area_geografica")[["eta_anni", "manutenzioni_ultimi_5anni", "guasto_entro_30gg"]].mean().round(2)
om, log, _ = nuovo_sistema()
om.imposta_promozioni(bd.gruppi_da_promuovere(cal.reset_index(), "area_geografica"), "calibrazione")
basso = om.sottometti(rac("AST-T5", "trasformatore", "Sud", p=0.05, c=0.95, azione="nessuna_azione"))
verifica("T5", bool(cal.loc["Sud", "allerta"]) and basso.livello.value == "HITL",
         f"Sud eta' {prof.loc['Sud', 'eta_anni']} vs Isole {prof.loc['Isole', 'eta_anni']}, guasti registrati "
         f"{prof.loc['Sud', 'guasto_entro_30gg']} vs {prof.loc['Isole', 'guasto_entro_30gg']}; gap calibrazione Sud "
         f"{cal.loc['Sud', 'gap_calibrazione']}; decisione HOTL del Sud promossa a {basso.livello.value}")
vigilate = bd.gruppi_recall_basso(bd.metriche_per_gruppo(pred, "area_geografica"), "area_geografica")
om.imposta_vigilanza(vigilate, "gap di recall")
routine = om.sottometti(rac("AST-T5b", "trasformatore", "Nord", p=0.15, c=0.85, azione="ispezione_routine"))
minimo = om.sottometti(rac("AST-T5c", "trasformatore", "Nord", p=0.05, c=0.95, azione="nessuna_azione"))
verifica("T5 recall basso", "Nord" in vigilate and routine.livello.value == "HITL"
         and minimo.livello.value == "HOTL" and om.kpi()["A6_copertura_routing"] == 1.0,
         f"aree vigilate {vigilate}; Nord p=0.15 -> {routine.livello.value}, p=0.05 -> {minimo.livello.value}; A6 = 100%")

print("\nT6 · Audit a ritroso")
om, log, _ = nuovo_sistema()
r = om.sottometti(rac("AST-T6", "cabina_primaria", "Centro"))
om.revisiona(r.id, S.MODIFICATA, "OP-014", "Ridotta a ispezione: manutenzione gia' pianificata a fine mese",
             azione_modificata="ispezione_routine")
record = [json.loads(l) for l in log.path.read_text(encoding="utf-8").splitlines()]
storia = [x for x in record if (x.get("decisione") or {}).get("asset_id") == "AST-T6"]
chiusa = storia[-1]
print(f"         chi {chiusa['attore']} · quando {chiusa['timestamp'][:19]} · cosa {chiusa['evento']} "
      f"(da {storia[0]['decisione']['azione']} a {chiusa['decisione']['azione']}) · perche' {chiusa['decisione']['motivazione']}")
copia = os.path.join(tempfile.mkdtemp(), "manomesso.jsonl")
shutil.copy(log.path, copia)
righe = open(copia, encoding="utf-8").read().splitlines()
alterata = json.loads(righe[-1])
alterata["decisione"]["motivazione"] = "Approvato"
righe[-1] = json.dumps(alterata, ensure_ascii=False)
open(copia, "w", encoding="utf-8").write("\n".join(righe) + "\n")
verifica("T6", log.verifica_catena()[0] and not AuditLogger(copia).verifica_catena()[0],
         "decisione ricostruita dal log; la modifica di una motivazione rompe la catena di hash")

falliti = [t for t, ok in esiti if not ok]
print(f"\nRISULTATO: {len(esiti) - len(falliti)}/{len(esiti)} verifiche superate" + (f" · FALLITI: {falliti}" if falliti else ""))
raise SystemExit(1 if falliti else 0)

"""
EnerGuard Starter Kit - Scheletro dashboard Streamlit
======================================================
Esecuzione:  streamlit run app.py
Prerequisito: aver eseguito train_baseline.py (genera predizioni.csv)

Lo scheletro definisce le SEZIONI OBBLIGATORIE della dashboard (vedi
documento "Indicatori di Qualita'"). Il come le realizzate e' scelta
vostra: Streamlit e' solo il default comodo, potete usare React/Gradio.
"""

import pandas as pd
import streamlit as st

from audit_logger import AuditLogger
from explainer import ConfigLLM, crea_spiegatore, estrai_fattori
from bias_detector import BiasDetector
from utils_io import carica_csv, prepara_feature
from oversight_manager import (OversightManager, Raccomandazione,
                               StatoDecisione, AZIONI, proponi_azione)

st.set_page_config(page_title="EnerGuard | Supervisione Umana",
                   layout="wide", page_icon="⚡")


# ----------------------------------------------------------------------
@st.cache_resource
def bootstrap():
    audit = AuditLogger("audit_trail.jsonl")
    om = OversightManager(audit)
    spiegatore = crea_spiegatore(audit)   # LLM se .env e' configurato, altrimenti template
    pred = carica_csv("predizioni.csv")
    bd = BiasDetector()
    cal = bd.calibrazione_per_gruppo(pred, "area_geografica")
    om.imposta_promozioni(bd.gruppi_da_promuovere(cal, "area_geografica"),
                          "gap di calibrazione oltre soglia (sospetto label bias)")
    # DECISIONE: 40 positive + 8 a basso rischio, altrimenti il ramo HOTL non viene mai esercitato
    campione = pd.concat([pred[pred["y_pred"] == 1].head(40),
                          pred[pred["proba"] < 0.2].head(8)])
    for _, riga in campione.iterrows():
        r = Raccomandazione(
            asset_id=riga["asset_id"],
            tipo_asset=riga["tipo_asset"],
            area_geografica=riga["area_geografica"],
            criticita_utenza=riga["criticita_utenza"],
            prob_guasto=round(float(riga["proba"]), 3),
            confidenza=round(float(riga["confidenza"]), 3),
            azione_proposta=proponi_azione(float(riga["proba"]), riga["criticita_utenza"]),
            spiegazione=[],  # TODO: riempire con SHAP/feature importance
        )
        om.sottometti(r)
    return om, audit, pred, spiegatore


om, audit, pred, spiegatore = bootstrap()

st.title("EnerGuard · Dashboard di Supervisione Umana")
operatore = st.sidebar.text_input("ID operatore", value="OP-001")

# --- EMERGENCY STOP: sempre visibile, mai a piu' di un click ---
st.sidebar.divider()
_cfg = ConfigLLM()
st.sidebar.caption(
    f"Motore spiegazioni: **{'LLM · ' + _cfg.descrizione() if _cfg.attivo else 'template locale'}**"
    + ("" if _cfg.attivo else "  \nConfigurate .env (vedi .env.example) per usare un LLM esterno."))

st.sidebar.subheader("Emergency stop")
ambito = st.sidebar.selectbox("Ambito", ["GLOBALE", "area:Sud", "area:Nord",
                                         "area:Centro", "area:Isole",
                                         "tipo:linea_AT", "tipo:trasformatore",
                                         "tipo:cabina_primaria", "tipo:turbina_eolica",
                                         "area:Sud+tipo:linea_AT"])
mot_stop = st.sidebar.text_input("Motivazione stop (min 15 caratteri)")
c1, c2 = st.sidebar.columns(2)
try:
    if c1.button("ATTIVA", type="primary"):
        n_bloccate = len(om.attiva_stop(ambito, operatore, mot_stop))
        st.sidebar.success(f"Stop {ambito} attivo: {n_bloccate} decisioni in coda bloccate.")
    if c2.button("Disattiva"):
        om.disattiva_stop(ambito, operatore, mot_stop)
except ValueError as e:
    st.sidebar.error(str(e))
if om.stop_attivi:
    st.sidebar.error(f"STOP ATTIVI: {', '.join(sorted(om.stop_attivi))}")

om.controlla_sla()

@st.cache_data(show_spinner=False)
def _fattori_asset(asset_id: str):
    """Estrae i fattori SHAP per un asset. In cache: SHAP e' costoso."""
    import joblib
    modello = joblib.load("modello.joblib")
    df = carica_csv("energuard_dataset.csv")
    X = prepara_feature(df)
    x = X.loc[df["asset_id"] == asset_id].iloc[0]
    return estrai_fattori(modello, x, list(X.columns))


def spiegazione_per(r):
    """Spiegazione in linguaggio operativo per una raccomandazione in coda."""
    rec = {"asset_id": r.asset_id, "tipo_asset": r.tipo_asset, "area_geografica": r.area_geografica,
           "criticita_utenza": r.criticita_utenza, "prob_guasto": r.prob_guasto,
           "confidenza": r.confidenza, "azione_proposta": r.azione_proposta,
           "livello": getattr(r.livello, "value", None), "soglia_confidenza": om.soglia_conf}
    return spiegatore.spiega(rec, _fattori_asset(r.asset_id))


tab_coda, tab_matrice, tab_bias, tab_audit, tab_kpi = st.tabs(
    ["Coda decisioni", "Matrice confidenza × rischio", "Bias & drift", "Audit trail",
     "KPI supervisione"])

# ----------------------------------------------------------------------
with tab_coda:
    pendenti = [r for r in om.coda
                if r.stato in (StatoDecisione.IN_ATTESA, StatoDecisione.ESCALATION)]
    st.metric("Decisioni in attesa di revisione umana", len(pendenti),
              delta=f"{sum(r.stato == StatoDecisione.ESCALATION for r in pendenti)} in escalation",
              delta_color="inverse")
    for r in sorted(pendenti, key=lambda x: -x.prob_guasto)[:10]:
        with st.expander(
                f"{'🔴' if r.livello.value == 'HIC' else '🟠'} {r.asset_id} · "
                f"{r.tipo_asset} · {r.area_geografica} · "
                f"P(guasto)={r.prob_guasto} · conf={r.confidenza} · {r.livello.value}"):
            st.write(f"Azione proposta: **{r.azione_proposta}** · "
                     f"Utenza: {r.criticita_utenza}")
            sp = spiegazione_per(r)
            st.markdown(sp.testo)
            st.warning(sp.incertezza)
            st.caption(f"Fonte spiegazione: {sp.fonte} · {sp.latenza_ms} ms")
            mot = st.text_area("Motivazione (obbligatoria)", key=f"m{r.id}")
            az = st.selectbox("Azione", AZIONI,
                              index=AZIONI.index(r.azione_proposta), key=f"a{r.id}")
            b1, b2, b3, b4 = st.columns(4)
            try:
                if b1.button("Approva", key=f"ok{r.id}"):
                    om.revisiona(r.id, StatoDecisione.APPROVATA, operatore, mot)
                    st.rerun()
                if b2.button("Modifica e approva", key=f"mod{r.id}"):
                    om.revisiona(r.id, StatoDecisione.MODIFICATA, operatore, mot,
                                 azione_modificata=az)
                    st.rerun()
                if b3.button("Rifiuta", key=f"no{r.id}"):
                    om.revisiona(r.id, StatoDecisione.RIFIUTATA, operatore, mot)
                    st.rerun()
                if b4.button("Escalation", key=f"esc{r.id}"):
                    om.revisiona(r.id, StatoDecisione.ESCALATION, operatore, mot)
                    st.rerun()
            except ValueError as e:
                st.error(str(e))

# ----------------------------------------------------------------------
with tab_matrice:
    st.subheader("Dove decide l'AI e dove serve l'umano")
    st.scatter_chart(pred.rename(columns={"proba": "rischio"}),
                     x="confidenza", y="rischio", color="area_geografica")
    st.caption("TODO: sovrapporre le soglie di routing HIC/HITL/HOTL e colorare "
               "le zone. L'operatore deve capire A COLPO D'OCCHIO in quale "
               "regime opera ogni decisione.")

# ----------------------------------------------------------------------
with tab_bias:
    bd = BiasDetector()
    valut = pred.rename(columns={})
    m = bd.metriche_per_gruppo(valut, "area_geografica")
    st.dataframe(m, use_container_width=True)
    for a in bd.allerte(m, "area_geografica"):
        st.warning(a)
    st.subheader("Calibrazione per area")
    cal = bd.calibrazione_per_gruppo(valut, "area_geografica")
    st.dataframe(cal, use_container_width=True)
    for a in bd.allerte_calibrazione(cal, "area_geografica"):
        st.error(a)
    if om.aree_promosse:
        st.info(f"Aree promosse a HITL (nessuna auto-esecuzione): {', '.join(sorted(om.aree_promosse))}")
    st.caption("TODO: aggiungere trend temporale (drift), tasso di override "
               "umano per area.")

# ----------------------------------------------------------------------
with tab_audit:
    ok, n = audit.verifica_catena()
    st.metric("Integrità catena audit", "VERIFICATA" if ok else "COMPROMESSA",
              delta=f"{n} record")
    st.caption("TODO: tabella filtrabile del log per asset/operatore/periodo.")

# ----------------------------------------------------------------------
with tab_kpi:
    k = om.kpi()
    st.subheader("Efficacia della supervisione")
    nd = lambda v: v if v is not None else "n/d"
    c1, c2, c3 = st.columns(3)
    c1.metric("A1 · Auto-esecuzioni improprie", k["A1_auto_esecuzione_impropria"],
              delta="target 0", delta_color="off")
    c2.metric("A2 · Tasso di override", nd(k["A2_tasso_override"]),
              delta="target 5-40%", delta_color="off")
    c3.metric("A3 · Tempo mediano revisione (s)", nd(k["A3_tempo_mediano_revisione_s"]),
              delta="target 30-300 s", delta_color="off")
    c4, c5, c6 = st.columns(3)
    c4.metric("A4 · Rubber-stamping", nd(k["A4_indice_rubber_stamping"]),
              delta="target < 10%", delta_color="off")
    c5.metric("A5 · Escalation SLA", nd(k["A5_tasso_escalation_sla"]),
              delta="target < 15%", delta_color="off")
    c6.metric("A6 · Copertura routing", nd(k["A6_copertura_routing"]),
              delta="target 100%", delta_color="off")
    st.caption("Distribuzione livelli: " + " · ".join(
        f"{l} {n}" for l, n in k["distribuzione_livelli"].items()))

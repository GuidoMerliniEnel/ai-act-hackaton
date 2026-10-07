# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Enel SpA
"""
EnerGuard Starter Kit - Scheletro dashboard Streamlit
======================================================
Esecuzione:  streamlit run app.py
Prerequisito: aver eseguito train_baseline.py (genera predizioni.csv)

Lo scheletro definisce le SEZIONI OBBLIGATORIE della dashboard (vedi
documento "Indicatori di Qualita'"). Il come le realizzate e' scelta
vostra: Streamlit e' solo il default comodo, potete usare React/Gradio.
"""

import altair as alt
import pandas as pd
import streamlit as st
from concurrent.futures import ThreadPoolExecutor

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
    promosse = bd.gruppi_da_promuovere(cal, "area_geografica")
    accuracy_rif = float((pred["y_pred"] == pred["y_true"]).mean())
    if bd.allerta_drift(bd.drift_settimanale(pred), accuracy_rif):
        promosse = sorted(pred["area_geografica"].unique())   # DECISIONE: drift = nessuna auto-esecuzione ovunque
    om.imposta_promozioni(promosse, "allerta di calibrazione o di drift (vedi scheda Bias & drift)")
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
            spiegazione=[],  # DECISIONE: fattori calcolati quando la card viene mostrata (SHAP costa ~1 s ad asset)
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
# DECISIONE: attivazione = 1 click + conferma (test T3); disattivazione = secondo operatore diverso
if st.sidebar.button("ATTIVA STOP", type="primary", width="stretch"):
    st.session_state["stop_da_confermare"] = ambito
if st.session_state.get("stop_da_confermare") == ambito:
    st.sidebar.warning(f"Confermi lo stop su **{ambito}**? Le decisioni in coda nell'ambito verranno bloccate.")
    k1, k2 = st.sidebar.columns(2)
    if k1.button("Conferma", type="primary"):
        try:
            n_bloccate = len(om.attiva_stop(ambito, operatore, mot_stop))
            st.session_state.pop("stop_da_confermare")
            st.session_state["esito_stop"] = f"Stop {ambito} attivo: {n_bloccate} decisioni in coda bloccate."
            st.rerun()
        except ValueError as e:
            st.sidebar.error(str(e))
    if k2.button("Annulla"):
        st.session_state.pop("stop_da_confermare")
        st.rerun()
if "esito_stop" in st.session_state:
    st.sidebar.success(st.session_state.pop("esito_stop"))
if om.stop_attivi:
    st.sidebar.error(f"STOP ATTIVI: {', '.join(sorted(om.stop_attivi))}")
    with st.sidebar.expander("Disattiva uno stop (doppia conferma)"):
        amb_off = st.selectbox("Stop da disattivare", sorted(om.stop_attivi))
        mot_off = st.text_input("Motivazione riattivazione (min 15 caratteri)")
        secondo = st.text_input("ID secondo operatore che conferma")
        presa_visione = st.checkbox("Ho verificato che la causa dello stop e' risolta")
        if st.button("Disattiva", disabled=not presa_visione):
            try:
                om.disattiva_stop(amb_off, operatore, mot_off, confermato_da=secondo)
                st.rerun()
            except ValueError as e:
                st.error(str(e))

om.controlla_sla()
_ok, _n = audit.verifica_catena()
st.sidebar.divider()
st.sidebar.caption(f"Audit trail: {'✅ catena integra' if _ok else '❌ CATENA COMPROMESSA'} · {_n} record")

@st.cache_data(show_spinner=False)
def _fattori_asset(asset_id: str):
    """Estrae i fattori SHAP per un asset. In cache: SHAP e' costoso."""
    import joblib
    modello = joblib.load("modello.joblib")
    df = carica_csv("energuard_dataset.csv")
    X = prepara_feature(df)
    x = X.loc[df["asset_id"] == asset_id].iloc[0]
    return estrai_fattori(modello, x, list(X.columns))


def spiegazione_per(r, fattori):
    """Spiegazione in linguaggio operativo per una raccomandazione in coda."""
    rec = {"asset_id": r.asset_id, "tipo_asset": r.tipo_asset, "area_geografica": r.area_geografica,
           "criticita_utenza": r.criticita_utenza, "prob_guasto": r.prob_guasto,
           "confidenza": r.confidenza, "azione_proposta": r.azione_proposta,
           "livello": getattr(r.livello, "value", None), "soglia_confidenza": om.soglia_conf}
    return spiegatore.spiega(rec, fattori)


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
    visibili = sorted(pendenti, key=lambda x: -x.prob_guasto)[:10]
    # DECISIONE: spiegazioni delle card visibili in parallelo, altrimenti ~3 s di LLM per card in sequenza
    fattori = [_fattori_asset(r.asset_id) for r in visibili]
    with ThreadPoolExecutor(max_workers=10) as pool:
        spiegazioni = dict(zip([r.id for r in visibili], pool.map(spiegazione_per, visibili, fattori)))
    for r in visibili:
        with st.expander(
                f"{'🔴' if r.livello.value == 'HIC' else '🟠'} {r.asset_id} · "
                f"{r.tipo_asset} · {r.area_geografica} · "
                f"P(guasto)={r.prob_guasto} · conf={r.confidenza} · {r.livello.value}"):
            st.write(f"Azione proposta: **{r.azione_proposta}** · "
                     f"Utenza: {r.criticita_utenza}")
            sp = spiegazioni[r.id]
            st.markdown(sp.testo)
            st.markdown("**Fattori principali:** " + " · ".join(
                f"{f.descrizione()} ({'aumenta' if f.contributo >= 0 else 'riduce'} il rischio)"
                for f in sp.fattori))
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

    bloccate = [r for r in om.coda if r.stato == StatoDecisione.BLOCCATA_STOP]
    if bloccate:
        st.subheader(f"Bloccate da emergency stop ({len(bloccate)})")
        st.caption("Restano bloccate anche dopo lo sblocco: rientrano solo se risottomesse, "
                   "e vengono rivalutate da zero.")
        for r in bloccate:
            c_info, c_mot, c_btn = st.columns([3, 3, 1])
            c_info.write(f"{r.asset_id} · {r.tipo_asset} · {r.area_geografica} · P={r.prob_guasto}")
            mot_r = c_mot.text_input("Motivazione", key=f"rs{r.id}", label_visibility="collapsed",
                                     placeholder="Motivazione risottomissione")
            if c_btn.button("Risottometti", key=f"rsb{r.id}"):
                try:
                    om.risottometti(r.id, operatore, mot_r)
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

# ----------------------------------------------------------------------
with tab_matrice:
    st.subheader("Dove decide l'AI e dove serve l'umano")
    # DECISIONE: colore = livello dalla matrice dichiarata (D3), cosi' il grafico mostra la stessa regola del codice
    mat = pred.rename(columns={"proba": "rischio"}).copy()
    mat["livello"] = [om.livello_dichiarato(Raccomandazione(
        r.asset_id, r.tipo_asset, r.area_geografica, r.criticita_utenza, r.rischio, r.confidenza,
        proponi_azione(r.rischio, r.criticita_utenza), [])).value for r in mat.itertuples()]
    colori = alt.Scale(domain=["HIC", "HITL", "HOTL"], range=["#d62728", "#ff9f1c", "#2ec4b6"])
    punti = alt.Chart(mat).mark_circle(size=45, opacity=0.75).encode(
        x=alt.X("confidenza", scale=alt.Scale(domain=[0.5, 1]), title="Confidenza del modello"),
        y=alt.Y("rischio", title="Probabilità di guasto a 30 giorni"),
        color=alt.Color("livello", scale=colori, title="Supervisione"),
        tooltip=["asset_id", "tipo_asset", "area_geografica", "criticita_utenza", "rischio", "livello"])
    soglie = (alt.Chart(pd.DataFrame({"x": [om.soglia_conf]})).mark_rule(strokeDash=[6, 4]).encode(x="x")
              + alt.Chart(pd.DataFrame({"y": [om.soglia_rischio]})).mark_rule(strokeDash=[6, 4]).encode(y="y"))
    st.altair_chart(punti + soglie, width="stretch")
    conteggi = mat["livello"].value_counts()
    c1, c2, c3 = st.columns(3)
    c1.metric("HIC · decide solo l'umano", int(conteggi.get("HIC", 0)))
    c2.metric("HITL · approvazione umana", int(conteggi.get("HITL", 0)))
    c3.metric("HOTL · AI agisce, umano monitora", int(conteggi.get("HOTL", 0)))
    st.caption(f"Linee tratteggiate: soglia di confidenza {om.soglia_conf} e di rischio {om.soglia_rischio}. "
               "Il rosso (utenze critiche) è sempre HIC, ovunque cada. "
               f"Aree senza auto-esecuzione per allerta: {', '.join(sorted(om.aree_promosse)) or 'nessuna'}.")

# ----------------------------------------------------------------------
with tab_bias:
    bd = BiasDetector()
    valut = pred.rename(columns={})
    m = bd.metriche_per_gruppo(valut, "area_geografica")
    st.dataframe(m, width="stretch")
    for a in bd.allerte(m, "area_geografica"):
        st.warning(a)
    st.subheader("Calibrazione per area")
    cal = bd.calibrazione_per_gruppo(valut, "area_geografica")
    st.dataframe(cal, width="stretch")
    for a in bd.allerte_calibrazione(cal, "area_geografica"):
        st.error(a)
    if om.aree_promosse:
        st.info(f"Aree promosse a HITL (nessuna auto-esecuzione): {', '.join(sorted(om.aree_promosse))}")

    st.subheader("Drift di performance · 12 settimane simulate")
    trend = bd.drift_settimanale(valut)
    rif = float((valut["y_pred"] == valut["y_true"]).mean())
    st.line_chart(trend.set_index("settimana")[["accuracy", "recall", "confidenza_media"]])
    allerta = bd.allerta_drift(trend, rif)
    if allerta:
        st.error(allerta)
    else:
        st.success(f"Nessun drift: accuracy mai sotto {round(rif - 0.10, 3)} per due settimane di fila "
                   f"(riferimento {round(rif, 3)}).")
    st.caption("Il dataset non ha date: le settimane sono blocchi consecutivi del test set (limite dichiarato).")

    st.subheader("Override umano per area")
    ovr = om.override_per_area()
    if ovr:
        st.dataframe(pd.DataFrame(ovr), width="stretch")
        for o in ovr:
            if o["allerta"]:
                st.error(f"OVERRIDE: in {o['area']} gli operatori correggono l'AI nel "
                         f"{o['tasso_override']:.0%} dei casi, oltre il doppio della media "
                         f"({o['media']:.0%}). Verificare il modello in quest'area.")
    else:
        st.caption("Nessuna decisione ancora revisionata.")

# ----------------------------------------------------------------------
with tab_audit:
    ok, n = audit.verifica_catena()
    st.metric("Integrità catena audit", "VERIFICATA" if ok else "COMPROMESSA",
              delta=f"{n} record")
    if not ok:
        st.error(f"Catena interrotta al record {n + 1}: il log è stato modificato dopo la scrittura.")
    st.caption("Ogni record contiene l'hash del precedente: modificare o cancellare una riga "
               "rompe la catena da quel punto in poi, e la verifica lo segnala.")

    righe = []
    for rec in audit._leggi():
        dec, ex = rec.get("decisione") or {}, rec.get("extra") or {}
        righe.append({"quando": rec["timestamp"][:19].replace("T", " "), "attore": rec["attore"],
                      "evento": rec["evento"], "asset_id": dec.get("asset_id") or ex.get("asset_id"),
                      "decisione": dec.get("id"), "livello": dec.get("livello"), "stato": dec.get("stato"),
                      "azione": dec.get("azione"), "motivazione": dec.get("motivazione") or ex.get("motivazione"),
                      "confermato_da": ex.get("confermato_da")})
    log = pd.DataFrame(righe)

    st.subheader("Ricostruisci una decisione")
    # DECISIONE: risposta a T6 in un passaggio: chi, cosa, quando, perche', AI approvata o corretta
    rev = log[log["evento"].str.startswith("revisione_")]
    if rev.empty:
        st.caption("Nessuna decisione ancora revisionata.")
    else:
        scelta = st.selectbox("Asset con decisione chiusa", rev["asset_id"].unique()[::-1])
        ultima = rev[rev["asset_id"] == scelta].iloc[-1]
        origine = log[(log["decisione"] == ultima["decisione"]) & log["evento"].str.startswith("in_coda")]
        proposta = origine["azione"].iloc[0] if not origine.empty else "n/d"
        esito = ultima["evento"].removeprefix("revisione_")
        giudizio = {"APPROVATA": "AI approvata", "MODIFICATA": "AI corretta",
                    "RIFIUTATA": "AI rifiutata"}.get(esito, esito)
        st.markdown(f"**Chi:** {ultima['attore']} · **Quando:** {ultima['quando']} · "
                    f"**Livello:** {ultima['livello']}  \n"
                    f"**Cosa:** {giudizio} — proposta AI `{proposta}`, azione finale `{ultima['azione']}`  \n"
                    f"**Perché:** {ultima['motivazione']}")
        st.dataframe(log[log["asset_id"] == scelta], width="stretch", hide_index=True)

    st.subheader("Log completo")
    f1, f2, f3, f4 = st.columns(4)
    f_asset = f1.text_input("Asset contiene")
    f_oper = f2.multiselect("Attore", sorted(log["attore"].unique()))
    giorni = pd.to_datetime(log["quando"]).dt.date
    f_per = f3.date_input("Periodo", value=(giorni.min(), giorni.max()))
    tecnici = f4.checkbox("Mostra eventi delle spiegazioni", value=False)
    vista = log.copy()
    if f_asset:
        vista = vista[vista["asset_id"].fillna("").str.contains(f_asset, case=False)]
    if f_oper:
        vista = vista[vista["attore"].isin(f_oper)]
    if isinstance(f_per, tuple) and len(f_per) == 2:
        vista = vista[pd.to_datetime(vista["quando"]).dt.date.between(*f_per)]
    if not tecnici:
        vista = vista[~vista["evento"].str.startswith("spiegazione_")]
    st.dataframe(vista.iloc[::-1], width="stretch", hide_index=True)
    e1, e2 = st.columns(2)
    e1.download_button("Esporta CSV per audit esterno", vista.to_csv(index=False), "audit_energuard.csv")
    e2.download_button("Esporta JSONL originale (con hash)", audit.path.read_text(encoding="utf-8"),
                       "audit_trail.jsonl")

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

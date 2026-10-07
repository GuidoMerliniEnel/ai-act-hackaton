"""
EnerGuard Starter Kit - OversightManager
=========================================
Gestisce il routing delle raccomandazioni AI verso i tre livelli di
supervisione (HIC / HITL / HOTL) e la coda di approvazione umana.

REGOLA D'ORO: nessuna azione con esito "IN_ATTESA" puo' essere eseguita.
Il vostro sistema deve dimostrarlo (la giuria lo testera' dal vivo).

TODO per il team:
  1. Completare la matrice di routing in `route()` giustificando le soglie
     nella Dichiarazione di Oversight (deliverable D3).
  2. Implementare l'escalation: una decisione HITL non revisionata entro
     `sla_minuti` deve cambiare stato, non essere eseguita in silenzio.
  3. Collegare ogni transizione di stato all'AuditLogger.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from statistics import median
from typing import Optional
import uuid


class LivelloSupervisione(str, Enum):
    HOTL = "HOTL"   # il sistema agisce, l'umano monitora ex post
    HITL = "HITL"   # approvazione umana obbligatoria prima dell'esecuzione
    HIC = "HIC"     # veto umano assoluto: solo l'umano decide


class StatoDecisione(str, Enum):
    IN_ATTESA = "IN_ATTESA"
    APPROVATA = "APPROVATA"
    MODIFICATA = "MODIFICATA"
    RIFIUTATA = "RIFIUTATA"
    ESCALATION = "ESCALATION"
    AUTO_ESEGUITA = "AUTO_ESEGUITA"   # ammessa SOLO per HOTL
    BLOCCATA_STOP = "BLOCCATA_STOP"   # bloccata da emergency stop
    RISOTTOMESSA = "RISOTTOMESSA"     # bloccata e poi rientrata nel flusso come nuova decisione


AZIONI = ["nessuna_azione", "ispezione_routine", "programma_manutenzione",
          "riduci_carico", "ispezione_urgente"]


def proponi_azione(prob: float, criticita: str) -> str:
    """DECISIONE: l'azione cresce col rischio; riduci_carico solo su utenza non standard (cosi' scatta HIC)."""
    if prob >= 0.85:
        return "riduci_carico" if criticita != "standard" else "ispezione_urgente"
    if prob >= 0.60:
        return "programma_manutenzione"
    if prob >= 0.10:
        return "ispezione_routine"
    return "nessuna_azione"


@dataclass
class Raccomandazione:
    asset_id: str
    tipo_asset: str
    area_geografica: str
    criticita_utenza: str          # standard | alta | critica
    prob_guasto: float             # output del modello, 0-1
    confidenza: float              # 0-1 (vedi nota in fondo)
    azione_proposta: str
    spiegazione: list              # es. [("vibrazione_indice", 0.41), ...]
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    creata_il: str = field(default_factory=lambda: datetime.now().isoformat())
    livello: Optional[LivelloSupervisione] = None
    stato: StatoDecisione = StatoDecisione.IN_ATTESA
    revisore: Optional[str] = None
    motivazione: Optional[str] = None
    chiusa_il: Optional[str] = None
    scaduta_sla: bool = False


class OversightManager:
    def __init__(self, audit_logger, soglia_confidenza_alta: float = 0.80,
                 soglia_rischio_alto: float = 0.60, sla_minuti: int = 30):
        self.audit = audit_logger
        self.soglia_conf = soglia_confidenza_alta
        self.soglia_rischio = soglia_rischio_alto
        self.sla_minuti = sla_minuti
        self.coda: list[Raccomandazione] = []
        self.storico_hotl: list[Raccomandazione] = []
        self.stop_attivi: set[str] = set()   # es. {"area:Sud", "tipo:linea_AT", "GLOBALE"}
        self.aree_promosse: set[str] = set()

    def imposta_promozioni(self, aree: list[str], motivo: str):
        """Aree in cui un'allerta (es. calibrazione) vieta l'auto-esecuzione HOTL."""
        nuove = set(aree)
        if nuove != self.aree_promosse:
            self.audit.log("SISTEMA", "promozione_HOTL_a_HITL", None,
                           extra={"aree": sorted(nuove), "motivo": motivo})
        self.aree_promosse = nuove

    # ------------------------------------------------------------------
    # ROUTING - il cuore dell'esercizio
    # ------------------------------------------------------------------
    def route(self, r: Raccomandazione) -> LivelloSupervisione:
        """Assegna il livello di supervisione. COMPLETARE E GIUSTIFICARE.

        Logica minima di partenza (da estendere):
          - utenza critica (ospedali, infrastrutture) o azione "riduci_carico"
            su utenza alta/critica  -> HIC, sempre
          - rischio alto O confidenza bassa                     -> HITL
          - rischio basso E confidenza alta E azione leggera    -> HOTL
        """
        if r.criticita_utenza == "critica" or (
                r.azione_proposta == "riduci_carico" and r.criticita_utenza != "standard"):
            livello = LivelloSupervisione.HIC
        elif r.prob_guasto >= self.soglia_rischio or r.confidenza < self.soglia_conf:
            livello = LivelloSupervisione.HITL
        elif r.area_geografica in self.aree_promosse:
            livello = LivelloSupervisione.HITL   # DECISIONE: area con allerta di bias, niente auto-esecuzione
        elif r.azione_proposta in ("nessuna_azione", "ispezione_routine"):
            livello = LivelloSupervisione.HOTL
        else:
            livello = LivelloSupervisione.HITL   # default prudente
        r.livello = livello
        return livello

    # ------------------------------------------------------------------
    def sottometti(self, r: Raccomandazione):
        """Instrada la raccomandazione e la esegue o la mette in coda."""
        self.route(r)
        if self._stop_applicabile(r):
            r.stato = StatoDecisione.BLOCCATA_STOP
            self.coda.append(r)   # visibile in coda: va risottomessa a mano dopo lo sblocco
            self.audit.log("SISTEMA", "blocco_emergency_stop", r)
            return r

        if r.livello == LivelloSupervisione.HOTL:
            r.stato = StatoDecisione.AUTO_ESEGUITA
            self._esegui(r)
            self.storico_hotl.append(r)
            self.audit.log("SISTEMA", "auto_esecuzione_HOTL", r)
        else:
            self.coda.append(r)
            self.audit.log("SISTEMA", f"in_coda_{r.livello.value}", r)
        return r

    def revisiona(self, decision_id: str, esito: StatoDecisione,
                  revisore: str, motivazione: str,
                  azione_modificata: Optional[str] = None):
        """Registra il giudizio umano. La motivazione e' OBBLIGATORIA."""
        if not motivazione or len(motivazione.strip()) < 15:
            raise ValueError("Motivazione obbligatoria (minimo 15 caratteri). "
                             "Senza motivazione non c'e' audit trail.")
        r = self._trova(decision_id)
        if r.stato not in (StatoDecisione.IN_ATTESA, StatoDecisione.ESCALATION):
            raise ValueError(f"Decisione {decision_id} gia' chiusa: {r.stato}")
        if self._stop_applicabile(r):  # DECISIONE: sotto stop nessuna revisione, altrimenti T3 e' aggirabile
            raise ValueError(f"Decisione {decision_id} nell'ambito di uno stop attivo: non revisionabile.")
        # DECISIONE: motivazione fotocopia di una gia' usata = giudizio non espresso (test T2, KPI A4)
        if self._normalizza(motivazione) in {self._normalizza(x.motivazione) for x in self.coda
                                             if x.motivazione and x.id != decision_id}:
            raise ValueError("Motivazione identica a una gia' usata: descrivete il caso specifico.")
        r.stato, r.revisore, r.motivazione = esito, revisore, motivazione
        if esito != StatoDecisione.ESCALATION:
            r.chiusa_il = datetime.now().isoformat()
        if azione_modificata:
            r.azione_proposta = azione_modificata
        if esito in (StatoDecisione.APPROVATA, StatoDecisione.MODIFICATA):
            self._esegui(r)
        self.audit.log(revisore, f"revisione_{esito.value}", r)
        return r

    # ------------------------------------------------------------------
    # EMERGENCY STOP - deve bloccare DAVVERO (la giuria lo verifica)
    # ------------------------------------------------------------------
    def attiva_stop(self, ambito: str, operatore: str, motivazione: str):
        """ambito: 'GLOBALE' | 'area:<nome>' | 'tipo:<tipo_asset>' | combinazione con '+'"""
        self._valida_motivazione(motivazione)
        self.stop_attivi.add(ambito)
        bloccate = []
        # DECISIONE: lo stop congela anche la coda esistente, non solo le nuove (test T3)
        for r in self.coda:
            if (r.stato in (StatoDecisione.IN_ATTESA, StatoDecisione.ESCALATION)
                    and self._match_ambito(ambito, r)):
                r.stato = StatoDecisione.BLOCCATA_STOP
                bloccate.append(r.id)
                self.audit.log(operatore, f"blocco_emergency_stop:{ambito}", r)
        self.audit.log(operatore, f"emergency_stop_ON:{ambito}", None,
                       extra={"motivazione": motivazione, "decisioni_bloccate": bloccate})
        return bloccate

    def disattiva_stop(self, ambito: str, operatore: str, motivazione: str,
                       confermato_da: str = ""):
        """DECISIONE: riattivazione a quattro occhi; le decisioni bloccate restano bloccate."""
        self._valida_motivazione(motivazione)
        if ambito not in self.stop_attivi:
            raise ValueError(f"Nessuno stop attivo per l'ambito {ambito}.")
        if not confermato_da.strip() or confermato_da.strip() == operatore.strip():
            raise ValueError("Serve la conferma di un secondo operatore, diverso da chi disattiva.")
        self.stop_attivi.discard(ambito)
        self.audit.log(operatore, f"emergency_stop_OFF:{ambito}", None,
                       extra={"motivazione": motivazione, "confermato_da": confermato_da.strip()})

    def risottometti(self, decision_id: str, operatore: str, motivazione: str) -> Raccomandazione:
        """Una decisione bloccata rientra nel flusso come nuova decisione, rivalutata da zero."""
        self._valida_motivazione(motivazione)
        vecchia = self._trova(decision_id)
        if vecchia.stato != StatoDecisione.BLOCCATA_STOP:
            raise ValueError(f"Decisione {decision_id} non bloccata: {vecchia.stato}")
        if self._stop_applicabile(vecchia):
            raise ValueError(f"Decisione {decision_id} ancora nell'ambito di uno stop attivo.")
        nuova = Raccomandazione(vecchia.asset_id, vecchia.tipo_asset, vecchia.area_geografica,
                                vecchia.criticita_utenza, vecchia.prob_guasto, vecchia.confidenza,
                                vecchia.azione_proposta, vecchia.spiegazione)
        vecchia.stato = StatoDecisione.RISOTTOMESSA
        self.audit.log(operatore, "risottomissione", vecchia,
                       extra={"motivazione": motivazione, "nuovo_id": nuova.id})
        return self.sottometti(nuova)

    @staticmethod
    def _normalizza(testo: Optional[str]) -> str:
        return " ".join((testo or "").lower().split())

    @staticmethod
    def _valida_motivazione(motivazione: str):
        if not motivazione or len(motivazione.strip()) < 15:
            raise ValueError("Motivazione obbligatoria (minimo 15 caratteri).")

    @staticmethod
    def _match_ambito(ambito: str, r: Raccomandazione) -> bool:
        """'area:Sud+tipo:linea_AT' vale solo se TUTTE le parti coincidono (AND)."""
        if ambito == "GLOBALE":
            return True
        chiavi = {f"area:{r.area_geografica}", f"tipo:{r.tipo_asset}"}
        return all(parte in chiavi for parte in ambito.split("+"))

    def _stop_applicabile(self, r: Raccomandazione) -> bool:
        return any(self._match_ambito(a, r) for a in self.stop_attivi)

    # ------------------------------------------------------------------
    def controlla_sla(self, adesso: Optional[datetime] = None) -> list[str]:
        """DECISIONE: oltre lo SLA la decisione va in ESCALATION e non viene mai eseguita in silenzio."""
        adesso = adesso or datetime.now()
        scadute = []
        for r in self.coda:
            if r.stato != StatoDecisione.IN_ATTESA:
                continue
            minuti = (adesso - datetime.fromisoformat(r.creata_il)).total_seconds() / 60
            if minuti > self.sla_minuti:
                r.stato = StatoDecisione.ESCALATION
                r.scaduta_sla = True
                scadute.append(r.id)
                self.audit.log("SISTEMA", "escalation_sla_scaduto", r,
                               extra={"minuti_in_attesa": round(minuti, 1)})
        return scadute

    # ------------------------------------------------------------------
    def _esegui(self, r: Raccomandazione):
        """Punto unico di esecuzione. Qualunque azione DEVE passare da qui.
        La giuria verifichera' che non esistano altri percorsi di esecuzione."""
        assert r.stato in (StatoDecisione.APPROVATA, StatoDecisione.MODIFICATA,
                           StatoDecisione.AUTO_ESEGUITA), \
            f"Tentata esecuzione con stato non valido: {r.stato}"
        assert not (r.livello == LivelloSupervisione.HIC
                    and r.stato == StatoDecisione.AUTO_ESEGUITA), \
            "Violazione: una decisione HIC non puo' mai essere auto-eseguita"
        assert not self._stop_applicabile(r), \
            f"Violazione: {r.asset_id} rientra in uno stop attivo"
        print(f"[ESECUZIONE] {r.asset_id}: {r.azione_proposta} ({r.livello.value})")

    def _trova(self, decision_id: str) -> Raccomandazione:
        for r in self.coda:
            if r.id == decision_id:
                return r
        raise KeyError(decision_id)

    # ------------------------------------------------------------------
    # KPI per il pannello di monitoraggio (vedi Indicatori di Qualita')
    # ------------------------------------------------------------------
    def kpi(self) -> dict:
        tutte = self.coda + self.storico_hotl
        supervisionate = [r for r in self.coda if r.livello in
                          (LivelloSupervisione.HIC, LivelloSupervisione.HITL)]
        # A1: HIC/HITL eseguite senza revisione umana (deve essere 0)
        improprie = [r for r in supervisionate
                     if r.stato == StatoDecisione.AUTO_ESEGUITA
                     or (r.stato in (StatoDecisione.APPROVATA, StatoDecisione.MODIFICATA)
                         and not r.revisore)]
        revisionate = [r for r in self.coda if r.stato in
                       (StatoDecisione.APPROVATA, StatoDecisione.MODIFICATA,
                        StatoDecisione.RIFIUTATA)]
        override = [r for r in revisionate if r.stato in
                    (StatoDecisione.RIFIUTATA, StatoDecisione.MODIFICATA)]
        durate = [(datetime.fromisoformat(r.chiusa_il)
                   - datetime.fromisoformat(r.creata_il)).total_seconds()
                  for r in revisionate if r.chiusa_il]
        viste, rubber = set(), 0
        for r in sorted(revisionate, key=lambda x: x.chiusa_il or ""):
            testo = (r.motivazione or "").strip().lower()
            if len(testo) < 30 or testo in viste:  # DECISIONE: breve o fotocopia = proxy di rubber-stamping (A4)
                rubber += 1
            viste.add(testo)
        hitl = [r for r in self.coda if r.livello == LivelloSupervisione.HITL]
        coerenti = sum(1 for r in tutte if r.livello == self.livello_dichiarato(r))
        pct = lambda n, d: round(n / d, 3) if d else None
        return {
            "in_attesa": sum(1 for r in self.coda if r.stato == StatoDecisione.IN_ATTESA),
            "A1_auto_esecuzione_impropria": len(improprie),
            "A2_tasso_override": pct(len(override), len(revisionate)),
            "A3_tempo_mediano_revisione_s": round(median(durate), 1) if durate else None,
            "A4_indice_rubber_stamping": pct(rubber, len(revisionate)),
            "A5_tasso_escalation_sla": pct(sum(r.scaduta_sla for r in hitl), len(hitl)),
            "A6_copertura_routing": pct(coerenti, len(tutte)),
            "distribuzione_livelli": {l.value: sum(1 for r in tutte if r.livello == l)
                                      for l in LivelloSupervisione},
            "stop_attivi": sorted(self.stop_attivi),
        }

    def override_per_area(self, min_revisioni: int = 3) -> list[dict]:
        """DECISIONE: allerta se un'area ha override oltre il doppio della media (esempio del canvas), con almeno 3 revisioni."""
        rev = [r for r in self.coda if r.stato in
               (StatoDecisione.APPROVATA, StatoDecisione.MODIFICATA, StatoDecisione.RIFIUTATA)]
        if not rev:
            return []
        ovr = lambda xs: sum(x.stato != StatoDecisione.APPROVATA for x in xs) / len(xs)
        media = ovr(rev)
        out = []
        for area in sorted({r.area_geografica for r in rev}):
            xs = [r for r in rev if r.area_geografica == area]
            tasso = ovr(xs)
            out.append({"area": area, "revisioni": len(xs), "tasso_override": round(tasso, 3),
                        "media": round(media, 3),
                        "allerta": len(xs) >= min_revisioni and media > 0 and tasso > 2 * media})
        return out

    def livello_dichiarato(self, r: Raccomandazione) -> LivelloSupervisione:
        """Matrice D3 in forma tabellare, indipendente da route(): serve a misurare A6."""
        if r.criticita_utenza == "critica":
            return LivelloSupervisione.HIC
        if r.azione_proposta == "riduci_carico" and r.criticita_utenza == "alta":
            return LivelloSupervisione.HIC
        leggera = r.azione_proposta in ("nessuna_azione", "ispezione_routine")
        if r.area_geografica in self.aree_promosse:
            return LivelloSupervisione.HITL
        if r.prob_guasto < self.soglia_rischio and r.confidenza >= self.soglia_conf and leggera:
            return LivelloSupervisione.HOTL
        return LivelloSupervisione.HITL


# NOTA SU "CONFIDENZA": per un classificatore binario una scelta semplice e
# difendibile e' confidenza = max(p, 1-p) oppure 1 - entropia normalizzata.
# Qualunque scelta va dichiarata nella model card.

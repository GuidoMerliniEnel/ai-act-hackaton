# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Enel SpA
"""
EnerGuard Starter Kit - BiasDetector
=====================================
Metriche di performance e fairness disaggregate per sottogruppo.
Un modello "accurato in media" puo' nascondere disparita' gravi:
questo modulo serve a renderle visibili nella dashboard.

DECISIONI del team:
  1. DECISIONE: metrica principale = gap di recall/FNR (il danno peggiore e' il guasto non previsto);
     la demographic parity resta solo come segnale di variabile proxy.
  2. DECISIONE: soglie 0.15 sul gap di recall e 0.10 sul gap di calibrazione; la seconda
     promuove a HITL le decisioni HOTL dell'area (OversightManager.imposta_promozioni).
  3. DECISIONE: Sud e Isole hanno profili quasi identici ma guasti registrati 0.24 contro 0.45:
     ipotesi di sotto-segnalazione al Sud, confermata dal solo gap di calibrazione del Sud.
"""

import pandas as pd
from typing import Optional
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             confusion_matrix)


class BiasDetector:
    def __init__(self, soglia_gap_recall: float = 0.15,
                 soglia_gap_selezione: float = 0.20,
                 soglia_gap_calibrazione: float = 0.10):
        self.soglia_gap_recall = soglia_gap_recall
        self.soglia_gap_selezione = soglia_gap_selezione
        self.soglia_gap_calibrazione = soglia_gap_calibrazione

    def metriche_per_gruppo(self, df: pd.DataFrame, col_gruppo: str,
                            col_y: str = "y_true",
                            col_pred: str = "y_pred") -> pd.DataFrame:
        righe = []
        for gruppo, sub in df.groupby(col_gruppo):
            tn, fp, fn, tp = confusion_matrix(
                sub[col_y], sub[col_pred], labels=[0, 1]).ravel()
            righe.append({
                col_gruppo: gruppo,
                "n": len(sub),
                "tasso_positivi_reali": round(sub[col_y].mean(), 3),
                "tasso_selezione": round(sub[col_pred].mean(), 3),  # per demographic parity
                "accuracy": round(accuracy_score(sub[col_y], sub[col_pred]), 3),
                "precision": round(precision_score(sub[col_y], sub[col_pred],
                                                   zero_division=0), 3),
                "recall": round(recall_score(sub[col_y], sub[col_pred],
                                             zero_division=0), 3),
                "fnr": round(fn / (fn + tp), 3) if (fn + tp) else None,
                "fpr": round(fp / (fp + tn), 3) if (fp + tn) else None,
            })
        return pd.DataFrame(righe).sort_values("recall")

    def allerte(self, metriche: pd.DataFrame, col_gruppo: str) -> list[str]:
        """Confronta ogni gruppo con il migliore e genera allerte testuali."""
        out = []
        m = metriche.dropna(subset=["recall"])
        if m.empty:
            return out
        best_recall = m["recall"].max()
        for _, r in m.iterrows():
            if best_recall - r["recall"] > self.soglia_gap_recall:
                out.append(
                    f"GAP RECALL: {col_gruppo}='{r[col_gruppo]}' ha recall "
                    f"{r['recall']} contro un massimo di {best_recall} "
                    f"(gap {round(best_recall - r['recall'], 3)} > soglia "
                    f"{self.soglia_gap_recall}). Rischio: guasti non previsti "
                    f"concentrati in questo sottogruppo.")
        gap_sel = m["tasso_selezione"].max() - m["tasso_selezione"].min()
        if gap_sel > self.soglia_gap_selezione:
            out.append(
                f"GAP SELEZIONE (demographic parity): differenza di "
                f"{round(gap_sel, 3)} nel tasso di interventi raccomandati tra "
                f"sottogruppi. Verificare se riflette rischio reale o bias "
                f"storico nei dati (variabile proxy).")
        return out

    def calibrazione_per_gruppo(self, df: pd.DataFrame, col_gruppo: str,
                                col_y: str = "y_true",
                                col_proba: str = "proba") -> pd.DataFrame:
        """Probabilita' media predetta contro tasso osservato: un gap isolato indica label bias."""
        c = df.groupby(col_gruppo).agg(proba_media=(col_proba, "mean"),
                                       tasso_osservato=(col_y, "mean"))
        c["gap_calibrazione"] = c["proba_media"] - c["tasso_osservato"]
        c["allerta"] = c["gap_calibrazione"].abs() > self.soglia_gap_calibrazione
        return c.round(3).reset_index()

    def gruppi_da_promuovere(self, calibrazione: pd.DataFrame, col_gruppo: str) -> list[str]:
        return calibrazione.loc[calibrazione["allerta"], col_gruppo].tolist()

    @staticmethod
    def drift_settimanale(df: pd.DataFrame, n_settimane: int = 12) -> pd.DataFrame:
        """Il dataset non ha date: il test set e' diviso in blocchi consecutivi come "settimane" simulate."""
        d = df.reset_index(drop=True)
        d["settimana"] = d.index * n_settimane // len(d) + 1
        return d.groupby("settimana").apply(lambda s: pd.Series({
            "accuracy": (s["y_pred"] == s["y_true"]).mean(),
            "recall": recall_score(s["y_true"], s["y_pred"], zero_division=0),
            "confidenza_media": s["confidenza"].mean()})).round(3).reset_index()

    @staticmethod
    def allerta_drift(trend: pd.DataFrame, riferimento: float, margine: float = 0.10,
                      consecutive: int = 2) -> Optional[str]:
        """DECISIONE: allerta se l'accuracy resta sotto riferimento - 0.10 per 2 settimane di fila (una sola = rumore)."""
        sotto = (trend["accuracy"] < riferimento - margine).astype(int)
        serie = sotto.groupby((sotto != sotto.shift()).cumsum()).cumsum()
        if (serie >= consecutive).any():
            sett = trend.loc[serie >= consecutive, "settimana"].tolist()
            return (f"DRIFT: accuracy sotto {round(riferimento - margine, 3)} per {consecutive} "
                    f"settimane consecutive (settimane {sett}). Decisioni HOTL promosse a HITL.")
        return None

    def allerte_calibrazione(self, calibrazione: pd.DataFrame, col_gruppo: str) -> list[str]:
        return [
            f"GAP CALIBRAZIONE: {col_gruppo}='{r[col_gruppo]}' ha probabilita' media "
            f"{r['proba_media']} contro {r['tasso_osservato']} osservato (gap "
            f"{r['gap_calibrazione']} > soglia {self.soglia_gap_calibrazione}). "
            f"Sospetto label bias: decisioni HOTL dell'area promosse a HITL."
            for _, r in calibrazione[calibrazione["allerta"]].iterrows()]

"""
EnerGuard Starter Kit - Baseline Tier 1
========================================
Modello di partenza + metriche disaggregate. Con questi parametri e il
dataset ufficiale dovreste ottenere AUC intorno a 0.85. Da qui in poi il
punteggio NON si vince migliorando l'AUC: si vince costruendo l'oversight.

Esecuzione:  python train_baseline.py
Output:      modello.joblib, predizioni.csv (input per la dashboard)
"""

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split

from bias_detector import BiasDetector
from utils_io import carica_csv, prepara_feature

# DECISIONE: costo FN ~10x FP; per utenze alte/critiche 0.20 perche' l'HIC protegge solo cio' che supera la soglia
SOGLIE = {"standard": 0.30, "alta": 0.20, "critica": 0.20}

df = carica_csv("energuard_dataset.csv")
y = df["guasto_entro_30gg"]
X = prepara_feature(df)

X_tr, X_te, y_tr, y_te, df_tr, df_te = train_test_split(
    X, y, df, test_size=0.3, random_state=0, stratify=y)

modello = RandomForestClassifier(
    n_estimators=300, random_state=0, class_weight="balanced")
modello.fit(X_tr, y_tr)

proba = modello.predict_proba(X_te)[:, 1]
pred = (proba >= df_te["criticita_utenza"].map(SOGLIE).values).astype(int)

print("AUC:", round(roc_auc_score(y_te, proba), 3))
print(classification_report(y_te, pred, digits=3))

# --- Metriche disaggregate: il deliverable chiave del Tier 1 ---
valut = df_te.copy()
valut["y_true"], valut["y_pred"], valut["proba"] = y_te.values, pred, proba

bd = BiasDetector()
for col in ["area_geografica", "tipo_asset", "criticita_utenza"]:
    m = bd.metriche_per_gruppo(valut, col)
    print(f"\n=== Metriche per {col} ===")
    print(m.to_string(index=False))
    for a in bd.allerte(m, col):
        print("  [ALLERTA]", a)

# Confidenza: scelta semplice, da dichiarare in model card
valut["confidenza"] = proba.round(3)
valut["confidenza"] = valut["proba"].apply(lambda p: round(max(p, 1 - p), 3))

joblib.dump(modello, "modello.joblib")
valut.to_csv("predizioni.csv", index=False)
print("\nSalvati: modello.joblib, predizioni.csv")

# ESITO INDAGINE Sud/Isole: profili quasi identici ma guasti registrati 0.24 contro 0.45 -> sospetta sotto-segnalazione al Sud.
# Mitigazioni: area fuori dal modello, soglie per criticita', allerta di calibrazione (vedi TRACCIAMENTO_MODIFICHE.md).

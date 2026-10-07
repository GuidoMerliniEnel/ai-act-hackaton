"""EnerGuard Starter Kit - lettura CSV robusta.
Accetta sia il CSV standard (separatore virgola, decimale punto) sia la
versione per Excel italiano (separatore punto e virgola, decimale virgola).
"""
import pandas as pd


def carica_csv(percorso: str) -> pd.DataFrame:
    df = pd.read_csv(percorso, encoding="utf-8-sig")
    if df.shape[1] == 1:  # tutto in una colonna: e' la versione ';' con decimale ','
        df = pd.read_csv(percorso, sep=";", decimal=",", encoding="utf-8-sig")
    return df


# DECISIONE: area_geografica fuori dal modello (proxy di label bias), resta nei dati per monitoraggio e stop
ESCLUSE_DAL_MODELLO = ["asset_id", "guasto_entro_30gg", "area_geografica"]


def prepara_feature(df: pd.DataFrame) -> pd.DataFrame:
    """Unico punto che costruisce le feature: training, dashboard e test devono coincidere."""
    return pd.get_dummies(df.drop(columns=ESCLUSE_DAL_MODELLO))

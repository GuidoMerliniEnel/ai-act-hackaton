# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Enel SpA
"""
EnerGuard Starter Kit - AuditLogger
====================================
Log append-only in JSONL con concatenazione di hash: ogni riga contiene
l'hash della precedente, quindi qualunque manomissione a posteriori rompe
la catena ed e' rilevabile. Risponde ai requisiti di tracciabilita'
(Art. 12 e Art. 14 AI Act).

DECISIONI del team:
  1. Tutte le transizioni di stato sono loggate dall'OversightManager: ingresso in coda,
     auto-esecuzioni HOTL, revisioni, escalation SLA, stop, sblocchi, risottomissioni (KPI D1).
  2. Integrita' della catena (`verifica_catena`) sempre visibile nella sidebar (D-30).
  3. Log filtrabile per asset, attore e periodo, con ricostruzione ed export nella scheda Audit (D-29).
  4. Scritture protette da lock per la generazione parallela delle spiegazioni (D-24).
"""

import hashlib
import json
import threading
from datetime import datetime
from pathlib import Path


class AuditLogger:
    def __init__(self, percorso: str = "audit_trail.jsonl"):
        self.path = Path(percorso)
        self._ultimo_hash = self._recupera_ultimo_hash()
        self._lock = threading.Lock()   # scritture concorrenti romperebbero la catena di hash

    def log(self, attore: str, evento: str, raccomandazione=None, extra: dict = None):
        with self._lock:
            return self._log(attore, evento, raccomandazione, extra)

    def _log(self, attore: str, evento: str, raccomandazione=None, extra: dict = None):
        record = {
            "timestamp": datetime.now().isoformat(),
            "attore": attore,                  # "SISTEMA" oppure id operatore
            "evento": evento,
            "hash_precedente": self._ultimo_hash,
        }
        if raccomandazione is not None:
            record["decisione"] = {
                "id": raccomandazione.id,
                "asset_id": raccomandazione.asset_id,
                "livello": getattr(raccomandazione.livello, "value", None),
                "stato": raccomandazione.stato.value,
                "azione": raccomandazione.azione_proposta,
                "prob_guasto": raccomandazione.prob_guasto,
                "confidenza": raccomandazione.confidenza,
                "motivazione": raccomandazione.motivazione,
            }
        if extra:
            record["extra"] = extra
        record["hash"] = self._hash(record)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._ultimo_hash = record["hash"]
        return record

    def verifica_catena(self) -> tuple[bool, int]:
        """Ritorna (integra?, n_record). Da mostrare nella dashboard."""
        precedente = "GENESI"
        n = 0
        for riga in self._leggi():
            atteso = riga.pop("hash")
            if riga.get("hash_precedente") != precedente or self._hash(riga) != atteso:
                return False, n
            precedente = atteso
            n += 1
        return True, n

    def _leggi(self):
        if not self.path.exists():
            return []
        return [json.loads(r) for r in self.path.read_text(encoding="utf-8").splitlines()]

    def _recupera_ultimo_hash(self) -> str:
        record = self._leggi()
        return record[-1]["hash"] if record else "GENESI"

    @staticmethod
    def _hash(record: dict) -> str:
        return hashlib.sha256(
            json.dumps(record, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()[:16]

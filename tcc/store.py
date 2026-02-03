from __future__ import annotations

import threading
from typing import Dict, Optional

from .models import TransactionRecord


class TCCStore:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._transactions: Dict[str, TransactionRecord] = {}

    def get(self, transaction_id: str) -> Optional[TransactionRecord]:
        with self._lock:
            return self._transactions.get(transaction_id)

    def save(self, record: TransactionRecord) -> None:
        with self._lock:
            self._transactions[record.transaction_id] = record

    def delete(self, transaction_id: str) -> None:
        with self._lock:
            self._transactions.pop(transaction_id, None)

    def list_ids(self) -> list[str]:
        with self._lock:
            return list(self._transactions.keys())

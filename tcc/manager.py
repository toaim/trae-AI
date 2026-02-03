from __future__ import annotations

from typing import Dict, Iterable

from .exceptions import (
    ParticipantFailure,
    TransactionAlreadyCompletedError,
    TransactionNotFoundError,
)
from .models import Participant, TransactionRecord, TransactionState
from .store import TCCStore


class TCCManager:
    def __init__(self, store: TCCStore | None = None) -> None:
        self._store = store or TCCStore()

    def begin(
        self,
        transaction_id: str,
        participants: Iterable[Participant],
        payload: Dict[str, object] | None = None,
    ) -> TransactionRecord:
        record = TransactionRecord(
            transaction_id=transaction_id,
            participants={p.name: p for p in participants},
            payload=payload if payload is not None else {},
        )
        self._store.save(record)
        return record

    def get(self, transaction_id: str) -> TransactionRecord:
        record = self._store.get(transaction_id)
        if record is None:
            raise TransactionNotFoundError(f"Transaction {transaction_id} not found")
        return record

    def try_all(self, transaction_id: str) -> TransactionRecord:
        record = self.get(transaction_id)
        if record.state in (TransactionState.CONFIRMED, TransactionState.CANCELED):
            raise TransactionAlreadyCompletedError(
                f"Transaction {transaction_id} already completed"
            )
        record.state = TransactionState.TRYING
        self._store.save(record)
        try:
            for participant in record.participants.values():
                participant.try_action(record.payload)
        except Exception as exc:  # noqa: BLE001 - surface root cause
            record.state = TransactionState.FAILED
            record.error = str(exc)
            self._store.save(record)
            self.cancel(transaction_id)
            raise ParticipantFailure(
                f"Participant failed during try: {exc}"
            ) from exc
        self._store.save(record)
        return record

    def confirm(self, transaction_id: str) -> TransactionRecord:
        record = self.get(transaction_id)
        if record.state == TransactionState.CONFIRMED:
            return record
        if record.state == TransactionState.CANCELED:
            raise TransactionAlreadyCompletedError(
                f"Transaction {transaction_id} already canceled"
            )
        for participant in record.participants.values():
            participant.confirm_action(record.payload)
        record.state = TransactionState.CONFIRMED
        self._store.save(record)
        return record

    def cancel(self, transaction_id: str) -> TransactionRecord:
        record = self.get(transaction_id)
        if record.state == TransactionState.CANCELED:
            return record
        if record.state == TransactionState.CONFIRMED:
            raise TransactionAlreadyCompletedError(
                f"Transaction {transaction_id} already confirmed"
            )
        for participant in record.participants.values():
            participant.cancel_action(record.payload)
        record.state = TransactionState.CANCELED
        self._store.save(record)
        return record

    def cleanup(self, transaction_id: str) -> None:
        self._store.delete(transaction_id)

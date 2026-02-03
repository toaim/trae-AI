from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, Optional


class TransactionState(str, Enum):
    PENDING = "pending"
    TRYING = "trying"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    FAILED = "failed"


@dataclass(frozen=True)
class Participant:
    name: str
    try_action: Callable[[Dict[str, object]], None]
    confirm_action: Callable[[Dict[str, object]], None]
    cancel_action: Callable[[Dict[str, object]], None]


@dataclass
class TransactionRecord:
    transaction_id: str
    participants: Dict[str, Participant]
    payload: Dict[str, object] = field(default_factory=dict)
    state: TransactionState = TransactionState.PENDING
    error: Optional[str] = None

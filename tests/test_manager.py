from tcc import Participant, TCCManager, TransactionState


def test_tcc_success_flow() -> None:
    payload: dict[str, object] = {}
    order = Participant(
        name="order",
        try_action=lambda data: data.setdefault("try", True),
        confirm_action=lambda data: data.update({"confirm": True}),
        cancel_action=lambda data: data.update({"cancel": True}),
    )
    manager = TCCManager()
    record = manager.begin("txn-success", [order], payload=payload)

    manager.try_all(record.transaction_id)
    manager.confirm(record.transaction_id)

    assert record.state == TransactionState.CONFIRMED
    assert payload["confirm"] is True


def test_tcc_failure_triggers_cancel() -> None:
    payload: dict[str, object] = {}

    def fail_try(_: dict[str, object]) -> None:
        raise RuntimeError("boom")

    order = Participant(
        name="order",
        try_action=fail_try,
        confirm_action=lambda data: data.update({"confirm": True}),
        cancel_action=lambda data: data.update({"cancel": True}),
    )

    manager = TCCManager()
    record = manager.begin("txn-fail", [order], payload=payload)

    try:
        manager.try_all(record.transaction_id)
    except Exception:
        pass

    assert record.state == TransactionState.CANCELED
    assert payload["cancel"] is True

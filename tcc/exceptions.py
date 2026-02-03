class TransactionNotFoundError(RuntimeError):
    pass


class TransactionAlreadyCompletedError(RuntimeError):
    pass


class ParticipantFailure(RuntimeError):
    pass

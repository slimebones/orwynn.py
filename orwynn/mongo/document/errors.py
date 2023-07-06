class InvalidIdError(Exception):
    """
    Cannot convert string id to object id.
    """
    def __init__(
        self,
        *,
        invalid_id: str
    ) -> None:
        message: str = f"cannot convert id <{invalid_id}> to ObjectId"
        super().__init__(message)


class InvalidOperatorError(Exception):
    """
    MongoDB operator is invalid.
    """
    def __init__(
        self,
        *,
        operator: str,
        explanation: str
    ):
        message: str = f"cannot accept operator <{operator}>: {explanation}"
        super().__init__(message)

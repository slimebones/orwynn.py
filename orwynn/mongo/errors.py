from pymongo.errors import DuplicateKeyError as PymongoDuplicateKeyError


class DuplicateKeyError(Exception):
    def __init__(
        self,
        message: str = "",
        original_error: PymongoDuplicateKeyError | None = None
    ) -> None:
        if not message and original_error:
            message = "; ".join([str(x) for x in original_error.args])
        super().__init__(message)


class DocumentUpdateError(Exception):
    pass

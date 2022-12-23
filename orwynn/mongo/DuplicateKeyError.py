from pymongo.errors import DuplicateKeyError as PymongoDuplicateKeyError
from orwynn.base.error.Error import Error


class DuplicateKeyError(Error):
    def __init__(
        self,
        message: str = "",
        original_error: PymongoDuplicateKeyError | None = None
    ) -> None:
        if not message and original_error:
            message = "; ".join(original_error.args)
        super().__init__(message)

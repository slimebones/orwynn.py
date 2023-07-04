from typing import TYPE_CHECKING
from pymongo.errors import DuplicateKeyError as PymongoDuplicateKeyError

if TYPE_CHECKING:
    from orwynn.mongo.document import Document


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


class UnsetIdDocumentError(Exception):
    """
    Id for document has not been set yet.
    """
    def __init__(
        self,
        *,
        explanation: str,
        document: "Document"
    ) -> None:
        message: str = \
            f"{explanation}: id for document <{document}> has not been set yet"
        super().__init__(message)

from typing import Any

from antievil import TypeConversionError
from pymongo.errors import DuplicateKeyError as PymongoDuplicateKeyError


class UnsetIdMongoError(Exception):
    """
    Id of created Mongo document should be set.
    """
    def __init__(self) -> None:
        super().__init__(
            "id of a created Mongo document should be set",
        )


class MongoTypeConversionError(TypeConversionError):
    """
    Cannot convert an input type to a mongo-compatible type.
    """
    def __init__(
        self,
        *,
        t: type,
    ):
        super().__init__(
            t1=t,
            reason="cannot convert to a mongo-compatible type",
        )


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


class UnsupportedQueryTypeError(Exception):
    """
    Type of given query is unsupported.
    """
    def __init__(
        self,
        *,
        key: str,
        unsupported_value: Any
    ) -> None:
        message: str = \
            f"query for key <{key}> has an unsupported value" \
            f" <{unsupported_value}>"
        super().__init__(message)

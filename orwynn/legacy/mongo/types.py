from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from orwynn.mongo import Document

MongoCompatibleType = str | int | float | bool | list | dict | None
TDocument = TypeVar("TDocument", bound="Document")

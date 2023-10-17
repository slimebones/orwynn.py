from typing import TypeVar

from orwynn.mongo import Document

MongoCompatibleType = str | int | float | bool | list | dict | None
TDocument = TypeVar("TDocument", bound=Document)

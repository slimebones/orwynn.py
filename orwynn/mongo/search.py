from typing import Generic

from orwynn.mongo.document import Document
from orwynn.mongo.types import TDocument
from orwynn.utils.dbsearch import DatabaseSearch


class DocumentSearch(DatabaseSearch[Document], Generic[TDocument]):
    """
    Search Mongo Documents.
    """


class MongoStateFlagSearch(DocumentSearch):
    keys: list[str] | None = None
    values: list[bool] | None = None

from typing import Any, Iterable, Self
from pymongo.cursor import Cursor
from orwynn.base.mapping.Mapping import Mapping

from orwynn.mongo.MongoDocument import MongoDocument
from orwynn.mongo.Mongo import Mongo
from orwynn.util import fmt


class MongoMapping(Mapping):
    """Mapping to work with MongoDB.

    Itself is some model representing MongoDB document and also has some class
    methods to manipulate with related document in DB and translate it from/to
    mapping.
    """
    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

    @classmethod
    def _collection(cls) -> str:
        return fmt.snakefy(cls.__name__)

    @classmethod
    def _mongo(cls) -> Mongo:
        return Mongo.ie()

    @classmethod
    def find_all(
        cls,
        query: dict,
        *args,
        **kwargs
    ) -> Iterable[Self]:
        cursor: Cursor = cls._mongo().find_all(
            cls._collection(), query, *args, **kwargs
        )

        return map(cls._parse_document, cursor)

    @classmethod
    def find_one(
        cls, query: dict, *args, **kwargs
    ) -> Self:
        return cls._parse_document(
            cls._mongo().find_one(cls._collection(), query, *args, **kwargs)
        )

    @classmethod
    def create(
        cls, mapping: Self, *args, **kwargs
    ) -> Self:
        return cls._parse_document(
            cls._mongo().create(
                cls._collection(), mapping.dict(), *args, **kwargs
            )
        )

    @classmethod
    def remove(
        cls, query: dict, *args, **kwargs
    ) -> Self:
        return cls._parse_document(
            cls._mongo().remove(
                cls._collection(), query, *args, **kwargs
            )
        )

    @classmethod
    def update(
        cls,
        query: dict,
        operation: dict,
        *args,
        **kwargs
    ) -> Self:
        return cls._parse_document(
            cls._mongo().update(
                cls._collection(), operation, query, *args, **kwargs
            )
        )

    @classmethod
    def _parse_document(cls, document: MongoDocument) -> Self:
        """Parses document to specified Model."""
        return cls.parse_obj(dict(document, id=document["_id"]))

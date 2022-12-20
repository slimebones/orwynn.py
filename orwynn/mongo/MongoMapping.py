from typing import Any, Iterable, Self

from bson import ObjectId
from pymongo.cursor import Cursor

from orwynn.base.mapping.Mapping import Mapping, if_linked
from orwynn.base.mapping.CustomUseOfMappingReservedFieldError import \
    CustomUseOfMappingReservedFieldError
from orwynn.mongo.Mongo import Mongo
from orwynn.mongo.MongoDocument import MongoDocument
from orwynn.util import fmt, validation


class MongoMapping(Mapping):
    """Mapping to work with MongoDB.

    Itself is some model representing MongoDB document and also has some class
    methods to manipulate with related document in DB and translate it from/to
    mapping.
    """
    def __init__(self, **data: Any) -> None:
        for k in data.keys():
            if k.startswith("mongo_"):
                raise CustomUseOfMappingReservedFieldError(
                    f"field {k} for mapping {self.__class__} is reserved,"
                    " your field keys shouldn't be prefixed with \"mongo_\""
                )
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
        **kwargs
    ) -> Iterable[Self]:
        cursor: Cursor = cls._mongo().find_all(
            cls._collection(),
            cls._adjust_id_to_mongo(kwargs),
        )

        return map(cls._parse_document, cursor)

    @classmethod
    def find_one(
        cls, **kwargs
    ) -> Self:
        return cls._parse_document(
            cls._mongo().find_one(
                cls._collection(),
                cls._adjust_id_to_mongo(kwargs),
            )
        )

    @if_linked
    def create(
        self
    ) -> Self:
        data: dict = self._adjust_id_to_mongo(self.dict())

        return self._parse_document(
            self._mongo().create(
                self._collection(), data
            )
        )

    @if_linked
    def remove(
        self, *args, **kwargs
    ) -> Self:
        id: str = validation.apply(self.id, str)
        return self._parse_document(
            self._mongo().remove(
                self._collection(), {"_id": id}, *args, **kwargs
            )
        )

    @if_linked
    def update(
        self,
        operation: dict,
        *args,
        **kwargs
    ) -> Self:
        id: str = validation.apply(self.id, str)
        return self._parse_document(
            self._mongo().update(
                self._collection(),
                {"_id": id},
                operation,
                *args,
                **kwargs
            )
        )

    @staticmethod
    def _adjust_id_to_mongo(data: dict) -> dict:
        if "id" in data:
            if data["id"] is not None:
                id: str = validation.apply(data["id"], str)
                data["_id"] = ObjectId(id)
            del data["id"]
        return data

    @staticmethod
    def _adjust_id_from_mongo(data: dict) -> dict:
        if "_id" in data:
            if data["_id"] is not None:
                data["id"] = str(data["_id"])
            del data["_id"]
        return data

    @classmethod
    def _parse_document(cls, document: MongoDocument) -> Self:
        """Parses document to specified Model."""
        return cls.parse_obj(cls._adjust_id_from_mongo(document))

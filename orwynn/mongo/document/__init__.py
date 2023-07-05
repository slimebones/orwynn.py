from types import NoneType
from typing import Any, Iterable, Self

from bson import ObjectId
from pydantic.fields import ModelField
from pymongo.cursor import Cursor
from pymongo.errors import DuplicateKeyError as PymongoDuplicateKeyError

from orwynn.di.di import Di
from orwynn.helpers.errors import UnsupportedError
from orwynn.mapping.errors import CustomUseOfMappingReservedFieldError
from orwynn.mapping.mapping import Mapping, if_linked
from orwynn.mongo.clientsession import ClientSession
from orwynn.mongo.document.helpers import convert_to_object_id
from orwynn.mongo.entity import MongoEntity
from orwynn.mongo.errors import (
    DocumentUpdateError,
    DuplicateKeyError,
    UnsetIdDocumentError,
)
from orwynn.mongo.mongo import Mongo
from orwynn.utils import validation
from orwynn.utils.fmt import snakefy


class Document(Mapping):
    """
    Mapping to work with MongoDB.

    Itself is some model representing MongoDB document and also has some class
    methods to manipulate with related document in DB and translate it from/to
    mapping.

    The ID of the document on creating is always a string, not ObjectId for
    adjusting convenience. Under the hood a convertation str->ObjectId is
    performed before saving to MongoDB and backwards ObjectId->str before
    forming the document from MongoDB data.
    """
    def __init__(self, **data: Any) -> None:
        for k in data:
            if k.startswith("mongo_"):
                raise CustomUseOfMappingReservedFieldError(
                    f"field {k} for mapping {self.__class__} is reserved,"
                    " your field keys shouldn't be prefixed with \"mongo_\""
                )
        super().__init__(**data)

    @classmethod
    def _get_collection(cls) -> str:
        return snakefy(cls.__name__)

    @classmethod
    def _get_mongo(cls) -> Mongo:
        return validation.apply(Di.ie().find("Mongo"), Mongo)

    @classmethod
    def start_session(cls, **kwargs) -> ClientSession:
        # Tip: In future here you can add per-document class defined session
        #   options to apply, so @classmethod is used instead of @staticmethod
        return cls._get_mongo().start_session(**kwargs)

    @classmethod
    def find_all(
        cls,
        query: dict | None = None,
        **kwargs
    ) -> Iterable[Self]:
        if query is None:
            query = {}
        validation.validate(query, dict)

        cursor: Cursor = cls._get_mongo().find_all(
            cls._get_collection(),
            cls._adjust_id_to_mongo(query),
            **kwargs
        )

        return map(cls._parse_document, cursor)

    @classmethod
    def find_one(
        cls,
        query: dict | None = None,
        **kwargs
    ) -> Self:
        if query is None:
            query = {}
        validation.validate(query, dict)

        return cls._parse_document(
            cls._get_mongo().find_one(
                cls._get_collection(),
                cls._adjust_id_to_mongo(query),
                **kwargs
            )
        )

    def getid(self) -> str:
        if self.id is None:
            raise UnsetIdDocumentError(
                explanation="cannot get an id",
                document=self
            )
        else:
            return self.id

    @if_linked
    def create(
        self,
        session: ClientSession | None = None
    ) -> Self:
        data: dict = self._adjust_id_to_mongo(self.dict())

        try:
            return self._parse_document(
                self._get_mongo().create_one(
                    self._get_collection(), data, session=session
                )
            )
        except PymongoDuplicateKeyError as error:
            raise DuplicateKeyError(original_error=error) from error

    @if_linked
    def remove(
        self, **kwargs
    ) -> Self:
        id: str = validation.apply(self.id, str)
        return self._parse_document(
            self._get_mongo().remove_one(
                self._get_collection(), {"_id": ObjectId(id)},
                **kwargs
            )
        )

    @if_linked
    def update(
        self,
        *,
        set: dict | None = None,
        inc: dict | None = None,
        **kwargs
    ) -> Self:
        """Updates document with given data.

        Args:
            set (optional):
                Which fields to set.
            inc (optional):
                Which fields to increment.
        """
        # Optimization tip: Consider adapting $inc in future for appropriate
        #   cases
        validation.validate(set, [dict, NoneType])
        validation.validate(inc, [dict, NoneType])

        id: str = validation.apply(self.id, str)

        operation: dict = {}
        if set is not None:
            self.__validate_update_dict(set)
            operation["$set"] = set
        if inc is not None:
            self.__validate_update_dict(inc)
            operation["$inc"] = inc

        return self._parse_document(
            self._get_mongo().update_one(
                self._get_collection(),
                {"_id": ObjectId(id)},
                operation,
                **kwargs
            )
        )

    @classmethod
    def _parse_document(cls, document: MongoEntity) -> Self:
        """Parses document to specified Model."""
        return cls.parse_obj(cls._adjust_id_from_mongo(document))

    @staticmethod
    def _adjust_id_to_mongo(data: dict) -> dict:
        if "id" in data:
            input_id_value: Any = data["id"]
            if input_id_value is not None:
                if (
                    isinstance(input_id_value, (str, dict, list))
                ):
                    data["_id"] = convert_to_object_id(input_id_value)
                else:
                    raise UnsupportedError(
                        title="field \"id\" with value",
                        value=input_id_value
                    )
            del data["id"]
        return data

    @staticmethod
    def _adjust_id_from_mongo(data: dict) -> dict:
        if "_id" in data:
            if data["_id"] is not None:
                data["id"] = str(data["_id"])
            del data["_id"]
        return data

    def __validate_update_dict(self, dct: dict) -> None:
        # WARNING: Don't use any removable checks like "assert" or "validation"
        #   since checks here should be performed in any case to avoid
        #   passing of dangerous updates to db.
        fields: dict[str, ModelField] = self.__fields__

        for k, v in dct.items():
            if k in fields:
                # Only strict checking should be performed
                if type(v) != fields[k].type_:
                    raise DocumentUpdateError(
                        f"unmatched given type {type(v)} to document type"
                        f" {fields[k].type_}"
                    )
            else:
                raise DocumentUpdateError(
                    f"key {k} is not present in document fields"
                )

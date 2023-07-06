import copy
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
from orwynn.mongo.document.errors import InvalidOperatorError
from orwynn.mongo.document.helpers import convert_to_object_id
from orwynn.mongo.entity import MongoEntity
from orwynn.mongo.errors import DocumentUpdateError, DuplicateKeyError
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
    def start_session(cls, **kwargs) -> ClientSession:
        # Tip: In future here you can add per-document class defined session
        #   options to apply, so @classmethod is used instead of @staticmethod
        return cls._get_mongo().start_session(**kwargs)

    @classmethod
    def get(
        cls,
        query: dict | None = None,
        **kwargs
    ) -> Iterable[Self]:
        """
        Fetches all instances matching the query for this document.

        Args:
            query(optional):
                MongoDB-compliant dictionary to search. By default all
                instances of the document is fetched.
            **kwargs(optional):
                Additional arguments to Mongo's find method.

        Returns:
            Iterable with the results of the search.
        """
        return cls.find_all(query, **kwargs)

    @classmethod
    def find_all(
        cls,
        query: dict | None = None,
        **kwargs
    ) -> Iterable[Self]:
        """
        @deprecated use Document.get instead
        """
        _query: dict = cls._parse_query(query)
        validation.validate(_query, dict)

        cursor: Cursor = cls._get_mongo().find_all(
            cls._get_collection(),
            cls._adjust_id_to_mongo(_query),
            **kwargs
        )

        return map(cls._parse_document, cursor)

    @classmethod
    def find_one(
        cls,
        query: dict | None = None,
        **kwargs
    ) -> Self:
        """
        @deprecated use Document.get instead and select as many instances as
        you might need
        """
        _query: dict = cls._parse_query(query)
        validation.validate(_query, dict)

        return cls._parse_document(
            cls._get_mongo().find_one(
                cls._get_collection(),
                cls._adjust_id_to_mongo(_query),
                **kwargs
            )
        )

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
        id: str = self.getid()
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
        operators: dict | None = None,
        **kwargs
    ) -> Self:
        """Updates document with given data.

        Args:
            set (optional):
                Which fields to set.
            inc (optional):
                Which fields to increment.
            operators(optional):
                Additional operators besides `$set` and `$inc` to add.
        """
        # Optimization tip: Consider adapting $inc in future for appropriate
        #   cases
        validation.validate(set, [dict, NoneType])
        validation.validate(inc, [dict, NoneType])

        id: str = self.getid()

        operation: dict = {}
        if set is not None:
            operation["$set"] = set
        if inc is not None:
            operation["$inc"] = inc
        if operators is not None:
            if "$set" in operators:
                raise InvalidOperatorError(
                    operator="$set",
                    explanation="pass it via keyword argument `set=`"
                )
            elif "$inc" in operators:
                raise InvalidOperatorError(
                    operator="$inc",
                    explanation="pass it via keyword argument `inc=`"
                )
            else:
                operation.update(operators)

        return self._parse_document(
            self._get_mongo().update_one(
                self._get_collection(),
                {"_id": ObjectId(id)},
                operation,
                **kwargs
            )
        )

    def refresh(
        self
    ) -> Self:
        """
        Refreshes the document with a new data from the database.
        """
        return self.find_one({
            "id": self.getid()
        })

    @classmethod
    def _get_collection(cls) -> str:
        return snakefy(cls.__name__)

    @classmethod
    def _get_mongo(cls) -> Mongo:
        return validation.apply(Di.ie().find("Mongo"), Mongo)

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
    def _parse_query(query: dict | None) -> dict:
        return {} if query is None else copy.copy(query)

    @staticmethod
    def _adjust_id_from_mongo(data: dict) -> dict:
        if "_id" in data:
            if data["_id"] is not None:
                data["id"] = str(data["_id"])
            del data["_id"]
        return data

from enum import Enum
import typing
from pydantic import BaseModel
from pykit.err import NotFoundErr
from orwynn import Cfg, Sys, Utils
from typing import Any, Callable, Iterable, Self, TypeVar, Generic

from pykit import validation

from pymongo import MongoClient as MongoClient
from pymongo import ReturnDocument as ReturnDocStrat
from pymongo.cursor import Cursor as MongoCursor
from pymongo.database import Database as MongoDb
from pymongo.client_session import ClientSession as MongoClientSession

from pykit.search import DatabaseSearch
from bson import ObjectId
from bson.errors import InvalidId
from pykit.types import T

MongoCompatibleType = str | int | float | bool | list | dict | None
MongoCompatibleTypes: tuple[Any, ...] = typing.get_args(MongoCompatibleType)

class Doc(BaseModel):
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
    sid: str = ""

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
        @deprecated use Doc.get instead and select as many instances as
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
        return FormatUtils.snakefy(cls.__name__)

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

TDoc = TypeVar("TDoc", bound=Doc)

class MongoSys(Sys):
    async def init(self):
        self._cfg: MongoCfg = self._cfg

        self._client: MongoClient = MongoClient(self._cfg.url)
        self._db: MongoDb = self._client[self._cfg.database_name]
        await MongoUtils.init(self._client, self._db)

class MongoUtils(Utils):
    _client: MongoClient
    _db: MongoDb

    @classmethod
    async def init(cls, client: MongoClient, db: MongoDb):
        cls._client = client
        cls._db = db

    @classmethod
    def drop_db(cls):
        cls._client.drop_database(cls._db)

    @classmethod
    def try_get(
        cls,
        collection: str,
        query: dict,
        **kwargs
    ) -> dict | None:
        validation.validate(collection, str)
        validation.validate(query, dict)

        result: Any | None = cls._db[collection].find_one(
            query, **kwargs
        )

        if result is None:
            return None

        assert isinstance(result, dict)
        return result

    @classmethod
    def get_many(
        cls,
        collection: str,
        query: dict,
        **kwargs
    ) -> MongoCursor:
        validation.validate(collection, str)
        validation.validate(query, dict)

        return cls._db[collection].find(
            query, **kwargs
        )

    @classmethod
    def create_one(
        cls,
        collection: str,
        data: dict,
        **kwargs
    ) -> dict:
        validation.validate(collection, str)
        validation.validate(data, dict)

        inserted_id: str = cls._db[collection].insert_one(
            data,
            **kwargs
        ).inserted_id

        # instead of searching for created document, just replace it's id
        # with mongo's generated one, which is better for performance
        copied: dict = data.copy()
        copied["_id"] = inserted_id
        return copied

    @classmethod
    def try_upd_one(
        cls,
        collection: str,
        query: dict,
        operation: dict,
        **kwargs
    ) -> dict | None:
        """Updates a document matching query and returns updated version."""
        validation.validate(collection, str)
        validation.validate(query, dict)
        validation.validate(operation, dict)

        upd_doc: Any = \
            cls._db[collection].find_one_and_update(
                query,
                operation,
                return_document=ReturnDocStrat.AFTER,
                **kwargs
            )

        if upd_doc is None:
            return None

        assert isinstance(upd_doc, dict)
        return upd_doc

    @classmethod
    def try_del_one(
        cls,
        collection: str,
        query: dict,
        **kwargs
    ) -> bool:
        validation.validate(collection, str)
        validation.validate(query, dict)

        removed_document: Any | None = \
            cls._db[collection].find_one_and_delete(
                query, **kwargs
            )

        if removed_document is None:
            return False

        return True

    @staticmethod
    def process_search(
        query: dict[str, Any],
        search: "DocSearch[TDoc]",
        doc_type: type[TDoc],
        *,
        find_all_kwargs: dict | None = None,
    ) -> list[TDoc]:
        if find_all_kwargs is None:
            find_all_kwargs = {}

        result: list[TDoc] = list(doc_type.get_many(
            query,
            **find_all_kwargs,
        ))

        if len(result) == 0:
            raise search.get_not_found_error("TDoc")
        if search.expectation is not None:
            search.expectation.check(result)

        return result

    @staticmethod
    def query_by_nested_dict(
        query: dict[str, Any],
        nested_dict: dict[str, Any],
        root_key: str,
    ) -> None:
        """
        Updates query for searching nested dict values.

        Args:
            query:
                Query to update.
            nested_dict:
                Data to search.
            root_key:
                Outermost key of field containing the nested dict.

        Example:
        ```python
        class MyDoc(Doc):
            mydata: dict

        query = {}
        nd = {
            "mycode": {
                "approximate": {
                    "$in": [12, 34]
                }
            }
        }
        root_key = "mydata"

        MongoUtils.query_by_nested_dict(
            query,
            nd,
            root_key
        )
        # query = {"mydata.mycode.approximate": {"$in": [12, 34]}}
        ```
        """
        converted_data: dict[str, Any] = MongoUtils.convert_dict({
            root_key: nested_dict,
        })
        query.update(converted_data)

    @staticmethod
    def convert_dict(d: dict[str, Any]) -> dict[str, Any]:
        """
        Converts dictionary into a Mongo search format.

        All key structures is converted to dot-separated string, e.g.
        `{"key1": {"key2": {"key3_1": 10, "key3_2": 20}}}` is converted to
        `{"key1.key2.key3_1": 10, "key1.key2.key3_2": 20}`.

        Keys started with dollar sign are not converted and left as it is:
        ```python
        # input
        {
            "a1": {
                "a2": {
                    "$in": my_list
                }
            }
        }

        # output
        {
            "a1.a2": {
                "$in": my_list
            }
        }
        ```
        """
        result: dict[str, Any] = {}

        for k, v in d.items():

            if k.startswith("$") or not isinstance(v, dict):
                result[k] = v
                continue

            for k1, v1 in MongoUtils.convert_dict(v).items():
                if k1.startswith("$"):
                    result[k] = {
                        k1: v1,
                    }
                    continue
                result[k + "." + k1] = v1

        return result

    @staticmethod
    def convert_compatible(obj: Any) -> MongoCompatibleType:
        """
        Converts object to mongo compatible type.

        Convertation rules:
        - object with type listed in already compatible mongo types is returned
        as it is
        - elements of list, as well as dictionary's keys and values are
        converted recursively using this function
        - in case of Enum, the Enum's value is obtained and converted through
        this function
        - objects with defined attribute `mongovalue` (either by variable or
        property) is called like `obj.mongovalue` and the result is converted
        again through this function
        - for all other types the MongoTypeConversionError is raised

        Args:
            obj:
                Object to convert.

        Raises:
            MongoTypeConversionError:
                Cannot convert object to mongo-compatible.
        """
        result: MongoCompatibleType

        if type(obj) is dict:
            result = {}
            for k, v in obj.items():
                result[MongoUtils.convert_compatible(k)] = \
                    MongoUtils.convert_compatible(v)
        elif type(obj) is list:
            result = []
            for item in obj:
                result.append(MongoUtils.convert_compatible(item))
        elif type(obj) in MongoCompatibleTypes:
            result = obj
        elif hasattr(obj, "mongovalue"):
            result = MongoUtils.convert_compatible(obj.mongovalue)
        elif isinstance(obj, Enum):
            result = MongoUtils.convert_compatible(obj.value)
        else:
            raise ValueError(f"cannot convert {type(obj)}")

        return result

    @staticmethod
    def refresh(doc: TDoc) -> TDoc:
        """
        Refreshes document with fresh data from database.
        """
        return doc.get({"id": doc.sid})

    @classmethod
    def convert_to_object_id(cls, obj: T) -> T | ObjectId:
        """
        Converts an object to ObjectId compliant.

        If the object is:
        - string: It is passed directly to ObjectId()
        - dict: All values are recursively converted using this method.
        - list: All items are recursively converted using this method.
        - other types: Nothing will be done.

        Returns:
            ObjectId-compliant representation of the given object.
        """
        result: T | ObjectId

        if type(obj) is str:
            try:
                result = ObjectId(obj)
            except InvalidId as error:
                raise ValueError(
                    f"{obj} has invalid id"
                ) from error
        elif type(obj) is dict:
            result = type(obj)()
            for k, v in obj.items():
                result[k] = MongoUtils.convert_to_object_id(v)
        elif type(obj) is list:
            result = type(obj)([
                MongoUtils.convert_to_object_id(x) for x in obj
            ])
        else:
            result = obj

        return result

class DocSearch(DatabaseSearch[Doc], Generic[TDoc]):
    """
    Search Mongo Docs.
    """

class MongoCfg(Cfg):
    url: str
    database_name: str



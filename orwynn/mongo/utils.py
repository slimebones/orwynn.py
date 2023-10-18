import typing
from enum import Enum
from typing import TYPE_CHECKING, Any

from orwynn.mongo.errors import (
    MongoTypeConversionError,
    UnsetIdMongoError,
)
from orwynn.mongo.types import MongoCompatibleType, TDocument
from orwynn.utils.klass import Static

if TYPE_CHECKING:
    from orwynn.mongo import Document
    from orwynn.mongo.search import DocumentSearch

MongoCompatibleTypes: tuple[Any, ...] = typing.get_args(MongoCompatibleType)


class MongoUtils(Static):
    @staticmethod
    def process_query(
        query: dict[str, Any],
        search: "DocumentSearch[TDocument]",
        DocumentClass: type[TDocument],
        *,
        find_all_kwargs: dict | None = None,
    ) -> list[TDocument]:
        if find_all_kwargs is None:
            find_all_kwargs = {}
        result: list[TDocument] = list(DocumentClass.find_all(
            query,
            **find_all_kwargs,
        ))

        if len(result) == 0:
            raise search.get_not_found_error("TDocument")
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
        class MyDocument(Document):
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
    def get_id(document: "Document") -> str:
        doc_id: str | None = document.id

        if doc_id is None:
            raise UnsetIdMongoError

        return doc_id

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
            raise MongoTypeConversionError(t=type(obj))

        return result

    @staticmethod
    def refresh(document: TDocument) -> TDocument:
        """
        Refreshes document with fresh data from database.
        """
        return document.find_one({"id": document.getid()})

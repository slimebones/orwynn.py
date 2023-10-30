from typing import Any, Callable

from pymongo import MongoClient, ReturnDocument
from pymongo.client_session import ClientSession
from pymongo.cursor import Cursor
from pymongo.database import Database as PymongoDatabase

from orwynn.base.database import Database
from orwynn.base.database.errors import DatabaseEntityNotFoundError
from orwynn.mongo.config import MongoConfig
from orwynn.mongo.entity import MongoEntity
from orwynn.utils import validation


class Mongo(Database):
    """Manages actions related to MongoDB."""
    def __init__(self, config: MongoConfig) -> None:
        self.__client: MongoClient = MongoClient(config.url)
        self.__database: PymongoDatabase = self.__client[config.database_name]
        self.start_session: Callable[[], ClientSession] = \
            self.__client.start_session

    def drop_database(self) -> None:
        self.__client.drop_database(self.__database)

    def find_all(
        self,
        collection: str,
        query: dict,
        **kwargs
    ) -> Cursor:
        validation.validate(collection, str)
        validation.validate(query, dict)

        return self.__database[collection].find(
            query, **kwargs
        )

    def find_one(
        self, collection: str, query: dict, **kwargs
    ) -> MongoEntity:
        validation.validate(collection, str)
        validation.validate(query, dict)

        result: Any | None = self.__database[collection].find_one(
            query, **kwargs
        )
        if result is None:
            raise DatabaseEntityNotFoundError(
                query=query, collection=collection
            )
        return validation.apply(result, dict)

    def create_one(
        self, collection: str, document: MongoEntity, **kwargs
    ) -> MongoEntity:
        """Creates a document returning it after creation."""
        validation.validate(collection, str)
        validation.validate(document, dict)

        inserted_id: str = self.__database[collection].insert_one(
            document, **kwargs
        ).inserted_id
        copied: MongoEntity = document.copy()

        # instead of searching for created document, just replace it's id
        # with mongo's generated one, which is better for performance
        copied["_id"] = inserted_id

        return copied

    def remove_one(
        self, collection: str, query: dict, **kwargs
    ) -> MongoEntity:
        """Deletes a document matching query and returns it."""
        validation.validate(collection, str)
        validation.validate(query, dict)

        removed_document: Any | None = \
            self.__database[collection].find_one_and_delete(
                query, **kwargs
            )

        if removed_document is None:
            raise DatabaseEntityNotFoundError(
                collection=collection, query=query
            )

        return validation.apply(removed_document, MongoEntity)

    def update_one(
        self,
        collection: str,
        query: dict,
        operation: dict,
        **kwargs
    ) -> MongoEntity:
        """Updates a document matching query and returns updated version."""
        validation.validate(collection, str)
        validation.validate(query, dict)
        validation.validate(operation, dict)

        updated_document: Any = \
            self.__database[collection].find_one_and_update(
                query,
                operation,
                return_document=ReturnDocument.AFTER,
                **kwargs
            )

        if updated_document is None:
            raise DatabaseEntityNotFoundError(
                collection=collection, query=query
            )

        return validation.apply(updated_document, MongoEntity)

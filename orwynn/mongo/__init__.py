from typing import Any

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.cursor import Cursor

from orwynn.base.database.DatabaseEntityNotFoundError import \
    DatabaseEntityNotFoundError
from orwynn.base.database import Database
from orwynn.mongo.MongoConfig import MongoConfig
from orwynn.mongo.MongoDocument import MongoDocument
from orwynn.util import validation


class Mongo(Database):
    """Manages actions related to MongoDB."""
    def __init__(self, config: MongoConfig) -> None:
        self.__client: MongoClient = MongoClient(config.uri)
        self.__database: Database = self.__client[config.database_name]

    def find_all(
        self,
        collection: str,
        query: dict,
        *args,
        **kwargs
    ) -> Cursor:
        validation.validate(collection, str)
        validation.validate(query, dict)

        return self.__database[collection].find(
            query, *args, **kwargs
        )

    def find_one(
        self, collection: str, query: dict, *args, **kwargs
    ) -> MongoDocument:
        validation.validate(collection, str)
        validation.validate(query, dict)

        result: Any | None = self.__database[collection].find_one(
            query, *args, **kwargs
        )
        if result is None:
            raise DatabaseEntityNotFoundError(
                query=query, collection=collection
            )
        return validation.cast(result, dict)

    def create(
        self, collection: str, document: MongoDocument, *args, **kwargs
    ) -> MongoDocument:
        """Creates a document returning it after creation."""
        validation.validate(collection, str)
        validation.validate(document, dict)

        return self.find_one(collection, {
            "_id": self.__database[collection].insert_one(
                    document, *args, **kwargs
                ).inserted_id
        })

    def remove(
        self, collection: str, query: dict, *args, **kwargs
    ) -> MongoDocument:
        """Deletes a document matching query and returns it."""
        validation.validate(collection, str)
        validation.validate(query, dict)

        removed_entity: dict | None = \
            self.__database[collection].find_one_and_delete(
                query, *args, **kwargs
            )

        if removed_entity is None:
            raise DatabaseEntityNotFoundError(
                collection=collection, query=query
            )

        return removed_entity

    def update(
        self,
        collection: str,
        query: dict,
        operation: dict,
        *args,
        **kwargs
    ) -> MongoDocument:
        """Updates a document matching query and returns updated version."""
        validation.validate(collection, str)
        validation.validate(query, dict)
        validation.validate(operation, dict)

        updated_entity: MongoDocument = \
            self.__database[collection].find_one_and_update(
                query, operation, *args, **kwargs
            )

        if updated_entity is None:
            raise DatabaseEntityNotFoundError(
                collection=collection, query=query
            )

        return updated_entity


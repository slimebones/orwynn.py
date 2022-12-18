from typing import Any
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.results import DeleteResult, UpdateResult
from orwynn.base.error.malfunction_error import MalfunctionError
from orwynn.util import validation
from orwynn.base.database.DatabaseEntityNotFoundError import DatabaseEntityNotFoundError
from orwynn.base.database.DatabaseService import DatabaseService
from orwynn.mongo.MongoConfig import MongoConfig


class MongoService(DatabaseService):
    """Manages actions related to MongoDB."""
    def __init__(self, config: MongoConfig) -> None:
        self.__client: MongoClient = MongoClient(config.uri)
        self.__database: Database = self.__client[config.database_name]

    def find(self, collection: str, query: dict, *args, **kwargs) -> dict:
        validation.validate(collection, str)
        validation.validate(query, dict)

        result: Any | None = self.__database[collection].find(
            query, *args, **kwargs
        )
        if result is None:
            raise DatabaseEntityNotFoundError(
                query=query, collection=collection
            )
        return validation.cast(result, dict)

    def find_one(self, collection: str, query: dict, *args, **kwargs) -> dict:
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

    def create(self, collection: str, entity: dict, *args, **kwargs) -> str:
        """Creates an entity returning it's id after creation."""
        validation.validate(collection, str)
        validation.validate(entity, dict)

        return validation.cast(
            self.__database[collection].insert_one(
                entity, *args, **kwargs
            ).inserted_id,
            str
        )

    def remove(self, collection: str, query: dict, *args, **kwargs) -> None:
        """Deletes an entity matching query."""
        validation.validate(collection, str)
        validation.validate(query, dict)

        result: DeleteResult = self.__database[collection].delete_one(
            query, *args, **kwargs
        )

        if result.deleted_count == 0:
            raise DatabaseEntityNotFoundError(
                query=query, collection=collection
            )
        elif result.deleted_count > 1:
            raise MalfunctionError(
                f"on method {self.remove} only one entity should be deleted"
            )

    def update(
        self,
        collection: str,
        query: dict,
        operation: dict,
        *args,
        **kwargs
    ) -> None:
        """Updates an entity matching query."""
        validation.validate(collection, str)
        validation.validate(query, dict)
        validation.validate(operation, dict)

        result: UpdateResult = self.__database[collection].update_one(
            query, operation, *args, **kwargs
        )

        if result.modified_count == 0:
            raise DatabaseEntityNotFoundError(
                f"no entities modified for query {query}"
                f" in collection {collection}"
            )
        elif result.modified_count > 1:
            raise MalfunctionError(
                f"on method {self.update} only one entity should be modified"
            )

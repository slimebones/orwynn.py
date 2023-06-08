from contextvars import ContextVar, Token
from typing import Any

from orwynn.base.worker.worker import Worker
from orwynn.utils import validation

from .errors import AlreadyInitializedStorageError, UndefinedStorageError


class ContextStorage(Worker):
    def __init__(self) -> None:
        self.__storage: ContextVar[dict | None] = ContextVar(
            "context_storage",
            default=None
        )

    def __get_storage_data_or_error(self) -> dict:
        storage_data: dict | None = self.__storage.get()

        if storage_data is None:
            raise UndefinedStorageError()

        return storage_data

    def init_data(
        self,
        initial_data: dict
    ) -> Token:
        """Initializes the context storage.

        Args:
            initial_data:
                Initial dictionary to set for the storage.

        Returns:
            Context token of the created storage.

        Raises:
            AlreadyInitializedStorageError:
                The storage is already initialized.
        """
        validation.validate(initial_data, dict)

        if self.__storage.get() is not None:
            raise AlreadyInitializedStorageError()

        return self.__storage.set(initial_data)

    def reset(
        self,
        token: Token
    ) -> None:
        """Resets the storage set related to given token.

        Args:
            token:
                Token related to storage's set to be reset.
        """
        validation.validate(token, Token)
        self.__storage.reset(token)

    def get(self, key: Any) -> Any:
        """Retrieves the value from storage by the key.

        Args:
            key:
                Key of the field to be retrieved.

        Returns:
            The value retrieved.

        Raises:
            UndefinedStorageError:
                Storage is not defined for current context.
            KeyError:
                No such key in storage.
        """
        storage_data: dict = self.__get_storage_data_or_error()
        try:
            return storage_data[key]
        except KeyError as err:
            raise KeyError(
                f"no such key {key} in storage"
            ) from err

    def save(self, key: Any, value: Any) -> None:
        """Saves a value for the key into the storage for the current context.

        Args:
            key:
                Key of the field to be saved.
            value:
                Value of the field to be saved.

        Raises:
            UndefinedStorageError:
                Storage is not defined for current context.
        """
        self.__get_storage_data_or_error()[key] = value

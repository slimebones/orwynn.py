from orwynn import rnd, validation
from orwynn.web import ContextStorage
from orwynn.web.context.RequestIdAlreadySavedError import (
    RequestIdAlreadySavedError,
)


class RequestContextId:
    def __init__(self) -> None:
        self.__storage: ContextStorage = ContextStorage.ie()

    def get(
        self
    ) -> str:
        return validation.apply(self.__storage.get("request_id"), str)

    def save(self) -> str:
        """Generates an id for the request and saves it into the context.

        Returns:
            Request id generated.

        Raises:
            RequestIdAlreadySavedError:
                If the request id has been set previously.
        """
        request_id: str = rnd.gen_id()
        try:
            self.__storage.get("request_id")
        except KeyError:
            self.__storage.save("request_id", request_id)
            return request_id
        else:
            raise RequestIdAlreadySavedError()
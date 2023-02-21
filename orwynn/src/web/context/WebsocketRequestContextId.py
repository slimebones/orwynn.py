from orwynn import validation
from orwynn.src.rnd.helpers import gen_id
from orwynn.src.web.context.ContextStorage import ContextStorage
from orwynn.src.web.context.RequestIdAlreadySavedError import (
    RequestIdAlreadySavedError,
)


class WebsocketRequestContextId:
    def __init__(self) -> None:
        self.__storage: ContextStorage = ContextStorage.ie()

    def get(
        self
    ) -> str:
        return validation.apply(
            self.__storage.get("websocket_request_id"),
            str
        )

    def save(self) -> str:
        """Generates an id for the request and saves it into the context.

        Returns:
            Request id generated.

        Raises:
            RequestIdAlreadySavedError:
                If the request id has been set previously.
        """
        request_id: str = gen_id()
        try:
            self.__storage.get("websocket_request_id")
        except KeyError:
            self.__storage.save("websocket_request_id", request_id)
            return request_id
        else:
            raise RequestIdAlreadySavedError()

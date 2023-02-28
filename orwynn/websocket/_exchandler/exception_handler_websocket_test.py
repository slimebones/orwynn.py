from orwynn.base.error import Error
from orwynn.base.exchandler._ExceptionHandler import ExceptionHandler
from orwynn.base.module._Module import Module
from orwynn.boot._Boot import Boot
from orwynn.proxy.BootProxy import BootProxy
from orwynn.util import validation
from orwynn.util.Protocol import Protocol
from orwynn.websocket import Websocket, WebsocketController


class SomeWebsocketError(Error):
    pass


class Wc(WebsocketController):
    ROUTE = "/"

    async def main(self, ws: Websocket) -> None:
        raise SomeWebsocketError("hello")


class Eh(ExceptionHandler):
    E = SomeWebsocketError
    PROTOCOL = Protocol.WEBSOCKET

    async def handle(
        self, request: Websocket, error: SomeWebsocketError
    ) -> None:
        data: dict = error.api
        data["value"]["message"] = "handled"
        await request.send_json(data)


def test_default():
    boot: Boot = Boot(
        Module("/", Controllers=[Wc])
    )

    with boot.app.client.websocket("/") as ws:
        data: dict = ws.receive_json()

        err = validation.apply(
            BootProxy.ie().api_indication.recover(
                SomeWebsocketError,
                data
            ),
            SomeWebsocketError
        )
        assert err.message == "hello"


def test_one_handler():
    boot: Boot = Boot(
        Module("/", Controllers=[Wc]),
        ExceptionHandlers={Eh}
    )

    with boot.app.client.websocket("/") as ws:
        data: dict = ws.receive_json()

        err = validation.apply(
            BootProxy.ie().api_indication.recover(
                SomeWebsocketError,
                data
            ),
            SomeWebsocketError
        )
        assert err.message == "handled"

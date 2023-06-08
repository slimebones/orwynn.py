from orwynn.base.errorhandler.errorhandler import ErrorHandler
from orwynn.base.module.module import Module
from orwynn.boot.boot import Boot
from orwynn.proxy.BootProxy import BootProxy
from orwynn.utils import validation
from orwynn.utils.Protocol import Protocol
from orwynn.websocket import Websocket, WebsocketController


class SomeWebsocketError(Exception):
    pass


class Wc(WebsocketController):
    ROUTE = "/"

    async def main(self, ws: Websocket) -> None:
        raise SomeWebsocketError("hello")


class Eh(ErrorHandler):
    E = SomeWebsocketError
    PROTOCOL = Protocol.WEBSOCKET

    async def handle(
        self, request: Websocket, error: SomeWebsocketError
    ) -> None:
        data: dict = BootProxy.ie().api_indication.digest(error)
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
        assert err.args[0] == "hello"


def test_one_handler():
    boot: Boot = Boot(
        Module("/", Controllers=[Wc]),
        ErrorHandlers={Eh}
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
        assert err.args[0] == "handled"

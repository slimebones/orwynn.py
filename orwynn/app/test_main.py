import pytest
from pytest import fixture

from orwynn.app.app import App
from orwynn.base.module import Module
from orwynn.boot import Boot
from orwynn.websocket import Websocket, WebsocketController


@fixture
def std_app(std_boot: Boot) -> App:
    return std_boot.app


@pytest.mark.asyncio
async def test_openapi(run_endpoint):
    data: dict = Boot.ie().app.client.get_jsonify("/openapi.json", 200)

    path: dict = data["paths"]["/"]["get"]
    assert path["deprecated"] is True
    assert path["tags"] == ["best-item", "buy-now"]
    assert \
        path["responses"]["201"]["description"] == "Best response description"
    assert \
        path["responses"]["201"]["description"] == "Best response description"


@pytest.mark.asyncio
async def test_get_dependant_patch_against_websocket():
    """
    Should correctly operate for websocket controllers and builtin middleware.
    """

    # FIXME:
    #   Due to strange reasons, this test works fine in orwynn environment,
    #   but gives an error related to fastapi.dependencies.utils.get_dependant
    #   function, which cannot handle _fw_handlers and other framework's
    #   related arguments.

    class WsCtrl(WebsocketController):
        Route = "/"

        async def main(self, websocket: Websocket) -> None:
            await websocket.send_json({"message": "hello"})

    boot: Boot = await Boot.create(
        Module("/", Controllers=[WsCtrl])
    )

    with boot.app.client.websocket("/") as ws:
        ws.receive_json()


@pytest.mark.asyncio
async def test_custom_docs_route():
    boot: Boot = await Boot.create(
        Module("/"),
        apprc={
            "prod": {
                "App": {
                    "docs_route": "/mydocs"
                }
            }
        }
    )

    # TODO: maybe to add checking that this is truly OpenAPI page returned,
    #       but now i'm too lazy for this
    boot.app.client.get("/mydocs", 200)


@pytest.mark.asyncio
async def test_custom_redoc_route():
    boot: Boot = await Boot.create(
        Module("/"),
        apprc={
            "prod": {
                "App": {
                    "redoc_route": "/myredoc"
                }
            }
        }
    )

    # TODO: maybe to add checking that this is truly ReDoc page returned,
    #       but now i'm too lazy for this
    boot.app.client.get("/myredoc", 200)

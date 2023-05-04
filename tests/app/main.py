from orwynn.apiversion import ApiVersion
from orwynn.app import App
from orwynn.base import Module
from orwynn.boot import Boot
from orwynn.http import HttpController, Endpoint, EndpointResponse


class DonutsController(HttpController):
    ROUTE = "/donuts"
    ENDPOINTS = [
        Endpoint(
            method="get",
            summary="Donuts!",
            tags=["donut"]
        )
    ]


def create_root_module() -> Module:
    return Module(
        "/",
        Providers=[

        ],
        Controllers=[
            DonutsController
        ],
        imports=[
        ]
    )


def create_boot() -> Boot:
    return Boot(
        create_root_module(),
        global_http_route="/api/v{version}",
        global_websocket_route="/ws/v{version}",
        api_version=ApiVersion(supported={1}),
    )


def create_app() -> App:
    return create_boot().app

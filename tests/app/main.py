from fastapi import Query
from orwynn.apiversion import ApiVersion
from orwynn.app import App
from orwynn.base import Module
from orwynn.boot import Boot
from orwynn.http import Endpoint, HttpController, LogMiddleware


class DonutsController(HttpController):
    ROUTE = "/donuts"
    ENDPOINTS = [
        Endpoint(
            method="get",
            summary="Donuts!",
            tags=["donut"]
        )
    ]

    def get(
        self,
        ids: list[str] | None = Query(None),
        amount: int | None = None,
        kind: str | None = None,
    ) -> dict:
        return {
            "ids": ids,
            "amount": amount,
            "kind": kind
        }


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
        global_middleware={
            LogMiddleware: ["*"]
        }
    )


def create_app() -> App:
    return create_boot().app

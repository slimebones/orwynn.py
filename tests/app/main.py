import asyncio

from fastapi import Query

from orwynn.apiversion import ApiVersion
from orwynn.base import Module
from orwynn.boot import Boot
from orwynn.http import (
    Endpoint,
    HttpController,
    LogMiddleware,
    RedirectHttpResponse,
)
from orwynn.server.engine import ServerEngine
from orwynn.server.server import Server


class DonutsController(HttpController):
    Route = "/donuts"
    Endpoints = [
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


class GoawayRedirectController(HttpController):
    Route = "/goaway"
    Endpoints = [
        Endpoint(
            method="get"
        )
    ]

    def get(self) -> RedirectHttpResponse:
        return RedirectHttpResponse("https://google.com")


def create_root_module() -> Module:
    return Module(
        "/",
        Providers=[

        ],
        Controllers=[
            DonutsController,
            GoawayRedirectController
        ],
        imports=[
        ]
    )


async def create_boot() -> Boot:
    return await Boot.create(
        create_root_module(),
        global_http_route="/api/v{version}",
        global_websocket_route="/ws/v{version}",
        api_version=ApiVersion(supported={1}),
        global_middleware={
            LogMiddleware: ["*"]
        }
    )


async def main():
    await Server(
        engine=ServerEngine.Uvicorn,
        boot=await create_boot()
    ).serve(
        host="localhost",
        port=8000
    )


if __name__ == "__main__":
    asyncio.run(main())

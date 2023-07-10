import asyncio

import uvicorn
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


class GoawayRedirectController(HttpController):
    ROUTE = "/goaway"
    ENDPOINTS = [
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
    config = uvicorn.Config(
        await create_boot(),
        port=8000,
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())

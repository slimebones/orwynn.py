from typing import Awaitable, Callable

from ryz.core import Res

from orwynn.sys import Sys, SysInp
from orwynn.yon.server.msg import Msg

Next = Callable[[SysInp], Awaitable[Res[Msg]]]
Middleware = Callable[[SysInp, Next], Awaitable[Res[Msg]]]

def construct(
    middlewares: list[Middleware], sys: Sys
) -> Next:
    async def inner(inp: SysInp) -> Res[Msg]:
        if len(middlewares) == 0:
            return await sys(inp)
        middleware = middlewares[0]
        next_middlewares = middlewares[1:]
        return await middleware(
            inp,
            construct(next_middlewares, sys)
        )
    return inner

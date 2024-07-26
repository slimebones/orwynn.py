from aiohttp import web
from pykit.code import Code
from rxcat import ServerBus


async def handle_get_codes(req: web.Request) -> web.Response:
    return web.json_response({
        "codes": (await (Code.get_regd_codes())).eject()
    })


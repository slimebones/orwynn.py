from aiohttp import web
from rxcat import ServerBus


async def handle_get_indexed_codes(req: web.Request) -> web.Response:
    bus = ServerBus.ie()
    return web.json_response({
        "indexed_mcodes": bus.INDEXED_MCODES,
        "indexed_errcodes": bus.INDEXED_ERRCODES
    })


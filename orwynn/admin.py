from aiohttp import web
from rxcat import ServerBus


async def handle_get_indexed_codes(request: web.Request) -> web.Response:
    bus = ServerBus.ie()
    return web.json_response({
        "indexedMcodes": bus.IndexedMcodes,
        "indexedErrcodes": bus.IndexedErrcodes
    })


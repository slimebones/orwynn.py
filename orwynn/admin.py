from aiohttp import web
from rxcat import ServerBus


async def handle_get_indexed_codes(req: web.Request) -> web.Response:
    print(f"server: {req.headers}")
    bus = ServerBus.ie()
    return web.json_response({
        "indexedMcodes": bus.IndexedMcodes,
        "indexedErrcodes": bus.IndexedErrcodes
    })


import aiohttp.web
from orwynn.boot import BootCfg
from orwynn.preload import handle_preload

default = [
    BootCfg(
        routedef_funcs=[
            lambda: aiohttp.web.post("/preload", handle_preload)
        ]
    )
]

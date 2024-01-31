import aiohttp.web
from orwynn.boot import BootCfg
from orwynn.mongo import MongoCfg
from orwynn.preload import handle_preload

default = [
    BootCfg(
        routedef_funcs=[
            lambda: aiohttp.web.post("/preload", handle_preload)
        ]
    ),
    MongoCfg(
        url="mongodb://localhost:9006",
        database_name="orwynn-test"
    )
]

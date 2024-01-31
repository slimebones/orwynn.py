import aiohttp.web

from orwynn.boot import BootCfg
from orwynn.mongo import MongoCfg
from orwynn.preload import PreloadCfg, handle_preload

default = [
    BootCfg(
        verbosity=2,
        routedef_funcs=[
            lambda: aiohttp.web.post("/preload", handle_preload)
        ]
    ),
    MongoCfg(
        url="mongodb://localhost:9006",
        database_name="orwynnTestDb",
        must_clean_db_on_destroy=True
    ),
    PreloadCfg(
        must_clean_preloads_on_destroy=True
    )
]

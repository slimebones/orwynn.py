import aiohttp.web
from orwynn.admin import handle_get_indexed_codes

from orwynn.boot import BootCfg
from orwynn.mongo import MongoCfg
from orwynn.preload import PreloadCfg, handle_preload

default = {
    "test": [
        BootCfg(
            std_verbosity=2,
            routedef_fns=[
                lambda: aiohttp.web.post("/preload", handle_preload),
                lambda: aiohttp.web.get(
                    "/admin/codes",
                    handle_get_indexed_codes
                )
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
}

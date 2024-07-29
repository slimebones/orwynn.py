from orwynn import AppCfg, RouteSpec
from orwynn.admin import handle_get_codes
from orwynn.mongo import MongoCfg
from orwynn.preload import PreloadCfg, handle_preload

default = {
    "test": [
        AppCfg(
            std_verbosity=2,
            route_specs=[
                RouteSpec(
                    method="post",
                    route="/preload",
                    handler=handle_preload
                ),
                RouteSpec(
                    method="get",
                    route="/admin/codes",
                    handler=handle_get_codes
                ),
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

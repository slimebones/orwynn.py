from typing import Callable
from orwynn.app.AppService import AppService
from orwynn.base.middleware.Middleware import Middleware
from orwynn.util import dt
from orwynn.util.http import Request, Response


class MainDispatcher(Middleware):
    """Central application middleware automatically added to handle all
    incoming requests and delegate them to user's middleware.
    """
    def __init__(self, app: AppService) -> None:
        super().__init__()
        self.app = app

    async def process(self, request: Request, call_next: Callable) -> Response:
        start_ts: float = dt.get_utc_timestamp()
        response: Response = await call_next(request)
        end_ts: float = dt.get_utc_timestamp()
        print(self.app)
        print(end_ts - start_ts)
        return response

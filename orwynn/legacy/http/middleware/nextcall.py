from collections.abc import Awaitable
from typing import Callable

from orwynn.http.requests import HttpRequest
from orwynn.http.responses import HttpResponse

# Callable function which returns an awaitable, see:
#   https://stackoverflow.com/a/59177557/14748231
HttpNextCall = Callable[[HttpRequest], Awaitable[HttpResponse]]

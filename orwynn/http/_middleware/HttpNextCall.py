from collections.abc import Awaitable
from typing import Callable

from orwynn.http import HttpRequest, HttpResponse

# Callable function which returns an awaitable, see:
#   https://stackoverflow.com/a/59177557/14748231
HttpNextCall = Callable[[HttpRequest], Awaitable[HttpResponse]]

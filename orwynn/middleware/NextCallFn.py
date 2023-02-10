from collections.abc import Awaitable
from typing import Callable

from orwynn.web import Request, Response

# Callable function which returns an awaitable, see:
#   https://stackoverflow.com/a/59177557/14748231
NextCallFn = Callable[[Request], Awaitable[Response]]

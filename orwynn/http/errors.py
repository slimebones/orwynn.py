from starlette.exceptions import HTTPException as StarletteHTTPException

from orwynn.base import Error

HttpException = StarletteHTTPException


class UnsupportedHttpMethodError(Error):
    pass

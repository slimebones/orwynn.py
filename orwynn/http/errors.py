from starlette.exceptions import HTTPException as StarletteHTTPException

from orwynn.base import Error
from ._endpoint.EndpointNotFoundError import EndpointNotFoundError

HttpException = StarletteHTTPException


class UnsupportedHttpMethodError(Error):
    pass

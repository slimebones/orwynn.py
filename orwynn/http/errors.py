from starlette.exceptions import HTTPException as StarletteHTTPException

from orwynn.base.error import Error
from ._controller.endpoint.errors import EndpointNotFoundError

HttpException = StarletteHTTPException


class UnsupportedHttpMethodError(Error):
    pass

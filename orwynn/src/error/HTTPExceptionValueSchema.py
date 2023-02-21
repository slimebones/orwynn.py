from orwynn.src.error.ErrorValueSchema import ErrorValueSchema


class HTTPExceptionValueSchema(ErrorValueSchema):
    status_code: int

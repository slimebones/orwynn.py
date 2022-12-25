from orwynn.base.error import ErrorValueSchema


class HTTPExceptionValueSchema(ErrorValueSchema):
    status_code: int

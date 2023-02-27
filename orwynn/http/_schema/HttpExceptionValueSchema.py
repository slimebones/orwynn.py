from orwynn.base.error.ErrorValueSchema import ErrorValueSchema


class HttpExceptionValueSchema(ErrorValueSchema):
    status_code: int

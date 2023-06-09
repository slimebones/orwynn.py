from orwynn.base.error import ErrorValueSchema


class HttpExceptionValueSchema(ErrorValueSchema):
    status_code: int

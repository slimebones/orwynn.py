from orwynn.base.errorValueSchema import ErrorValueSchema


class HttpExceptionValueSchema(ErrorValueSchema):
    status_code: int

from orwynn.error.ErrorValueSchema import ErrorValueSchema


class RequestValidationExceptionValueSchema(ErrorValueSchema):
    locations: list[list[str | int]]

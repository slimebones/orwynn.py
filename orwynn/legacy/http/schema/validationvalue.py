from orwynn.error import ErrorValueSchema


class RequestValidationExceptionValueSchema(ErrorValueSchema):
    locations: list[list[str | int]]

from orwynn.base.errorValueSchema import ErrorValueSchema


class RequestValidationExceptionValueSchema(ErrorValueSchema):
    locations: list[list[str | int]]

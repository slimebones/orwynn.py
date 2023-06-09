from orwynn.base.model import Model

from .response import EndpointResponse


class Endpoint(Model):
    """Specification of endpoint.

    Attributes:
        method:
            Method to be used for this endpoint.
        default_status_code (optional):
            Status code to be returned by default from the endpoint. Defaults
            to 200.
        summary (optional):
            Short description of the endpoint. Note that full description is
            taken from the endpoint's docstring. Defaults to pattern summary
            depending on given envpoint's method, e.g. for method POST you
            will get summary "Create {your_model_name}".
        tags (optional):
            List of tags to apply for this endpoint. Empty by default
        is_deprecated (optional):
            Whether this route is deprecated. Defaults to False.
        responses (optional):
            Map with responses representations by their status codes. Defaults
            to built in framework basic responses.
    """
    method: str
    default_status_code: int = 200
    summary: str | None = None
    tags: list[str] | None = None
    is_deprecated: bool = False
    responses: list[EndpointResponse] | None = None

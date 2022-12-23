from orwynn.base.controller.endpoint.EndpointSpecResponses import \
    EndpointSpecResponses
from orwynn.base.model.Model import Model


class EndpointSpec(Model):
    """Specification of endpoint.

    Attributes:
        ResponseModel (optional):
            Model to expect to be returned from this endpoint. Final content
            returned will be api-indication based data created from this model.
            By default returned data from endpoint is not checked against any
            model or indication.
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
        response_description (optional):
            Description of response. Mostly used in OpenAPI. Defaults to
            "Successful response". For other response' descriptions of the same
            endpoint use "responses" argument.
        is_deprecated (optional):
            Whether this route is deprecated. Defaults to False.
        responses (optional):
            Map with responses representations by their status codes. Defaults
            to built in framework basic responses.
    """
    ResponseModel: type[Model] | None = None
    default_status_code: int = 200
    summary: str | None = None
    tags: list[str] | None = None
    response_description: str = "Successful response"
    is_deprecated: bool = False
    responses: EndpointSpecResponses | None = None

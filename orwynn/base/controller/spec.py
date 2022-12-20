import functools
from types import NoneType
from typing import Callable

from orwynn.base.controller.SpecResponses import SpecResponses
from orwynn.base.model.Model import Model
from orwynn.util import validation


def spec(
    *,
    response_model: Model | None = None,
    default_status_code: int = 200,
    summary: str | None = None,
    tags: list[str] | None = None,
    response_description: str = "Successful response",
    is_deprecated: bool = False,
    responses: SpecResponses | None = None
) -> Callable:
    """Attaches spec for endpoint.

    Args:
        response_model (optional):
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
    def wrapper(fn: Callable):
        @functools.wraps(fn)
        def inner(*args, **kwargs) -> Callable:
            return fn(*args, **kwargs)

        return inner

    validation.validate(response_model, [Model, NoneType])
    validation.validate(default_status_code, int)
    validation.validate(summary, [str, NoneType])
    if tags is not None:
        validation.validate_each(tags, str, expected_obj_type=list)
    validation.validate(response_description, str)
    validation.validate(is_deprecated, bool)
    if responses is not None:
        validation.validate_dict(responses, (int, validation.Validator.SKIP))

    return wrapper

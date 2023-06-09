import inspect
import typing
from types import NoneType, UnionType

from orwynn.utils.url import UrlVars
from orwynn.websocket.websocket import Websocket

from .handlers import WebsocketHandler

# Types allowed to be set at handler's function argument annotations
_AllowedTypesUnion = str | int | float
_AllowedTypes: tuple[type] = typing.get_args(_AllowedTypesUnion)
_Annotation = typing.TypeVar("_Annotation")

# Allowed for handler kwargs
HandlerKwargs = dict[str, _AllowedTypesUnion]


def get_handler_kwargs(
    handler: WebsocketHandler,
    url_vars: UrlVars
) -> HandlerKwargs:
    """
    Inspects the given handler and the given url vars to select and convert
    kwargs required by the handler.

    Args:
        handler:
            Websocket handler to inspect.
        url_vars:
            Collected url variables to select from.

    Returns:
        Kwargs dictionary.
    """
    kwargs: HandlerKwargs = {}


    for param in inspect.signature(handler.fn).parameters.values():
        _check_if_duplicate(
            kwargs=kwargs,
            param=param
        )

        if param.annotation is Websocket:
            continue
        elif (
            type(param.annotation) is UnionType
            and any([
                a in _AllowedTypes
                    for a in typing.get_args(param.annotation)
            ])
        ):
            _set_union_param(
                kwargs=kwargs,
                param=param,
                handler=handler,
                url_vars=url_vars
            )
        elif (
            type(param.annotation) is type
            and param.annotation in _AllowedTypes
        ):
            _set_regular_param(
                kwargs=kwargs,
                param=param,
                url_vars=url_vars
            )
        else:
            raise TypeError(
                f"unsupported param with name {param.name} annotation:"
                f" {param.annotation}"
            )

    return kwargs


def _set_regular_param(
    *,
    kwargs: HandlerKwargs,
    param: inspect.Parameter,
    url_vars: UrlVars
) -> None:
    try:
        path_var_value: str = url_vars.path_vars[param.name]
    except KeyError as err:
        # Path variables unlike query ones cannot be defaulted, so here we
        # raise an error
        raise KeyError(
            f"no path variable for name: {param.name}"
        ) from err
    else:
        kwargs[param.name] = _convert_var_value(
            path_var_value,
            Annotation=param.annotation
        )


def _set_union_param(
    *,
    kwargs: HandlerKwargs,
    param: inspect.Parameter,
    handler: WebsocketHandler,
    url_vars: UrlVars
) -> None:
    union_args: tuple = param.annotation.__args__
    _check_union_args(
        union_args,
        handler=handler,
        param=param
    )

    final_value: typing.Any
    try:
        # For union types we operate only with query args
        query_var_value: str = url_vars.query_vars[param.name]

        # Choose non-None element of the union
        PositiveAnnotation: type = \
            union_args[0] if union_args[0] is not NoneType else union_args[1]

        final_value = _convert_var_value(
            query_var_value,
            Annotation=PositiveAnnotation
        )
    except KeyError:
        # Query variables can be omitted: in this case we use default
        # values specified in annotation
        #
        # Also, in the default case no convertation is required since it should
        # be a plain python object which came from the code
        final_value = param.default

    kwargs[param.name] = final_value


def _check_union_args(
    union_args: tuple,
    *,
    handler: WebsocketHandler,
    param: inspect.Parameter
) -> None:
    if param.default is inspect._empty:
        raise ValueError(
            f"handler {handler} param {param.name} with union annotation"
            f" {param.annotation} should have default value since"
            " it will be filled from an optional query"
        )
    elif (
        type(param.default) not in _AllowedTypes
        and param.default is not None
    ):
        raise TypeError(
            f"parameter's default {param.default} is neither in allowed types"
            f" {_AllowedTypes} nor is None"
        )
    elif len(union_args) != 2:
        raise ValueError(
            "only strict unions are allowed: length of handler"
            f" {handler} param {param.name}"
            f" annotation {param.annotation} should equal 2"
        )
    elif NoneType not in union_args:
        raise TypeError(
            f"handler {handler} param {param.name} annotation"
            f" {param.annotation} union args {union_args} should "
            " contain None at any position"
        )
    elif (
        union_args[0] not in _AllowedTypes
        and union_args[1] not in _AllowedTypes
    ):
        raise TypeError(
            f"parameter {param.name} have unsupported element in union"
            f" annotation {param.annotation}"
        )


def _check_if_duplicate(
    *,
    kwargs: HandlerKwargs,
    param: inspect.Parameter
) -> None:
    if param.name in kwargs:
        raise ValueError(
            f"variable {param.name} has been already set in handler kwargs"
        )


def _convert_var_value(
    value: str,
    *,
    Annotation: type[_Annotation]
) -> _Annotation:
    # Apply convertation to one of the allowed formats, now it can be done
    # directly with annotation (after the checks made of course), e.g.
    # with int annotation it would be int(VARIABLE)
    return Annotation(value)

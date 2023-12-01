from typing import Any, Callable

from fastapi.dependencies.models import Dependant
from fastapi.dependencies.utils import (
    add_non_field_param_to_dependency,
    add_param_to_fields,
    analyze_param,
    get_param_sub_dependant,
    get_typed_signature,
    is_body_param,
)
from fastapi.utils import get_path_param_names


def get_dependant(
    *,
    path: str,
    call: Callable[..., Any],
    name: str | None = None,
    security_scopes: list[str] | None = None,
    use_cache: bool = True,
) -> Dependant:

    # Copy of FastAPI code in order to add some logic (very bad we know).
    # Custom logic marked with (ORWYNN).
    #
    # Changed 2023-12-03 to comply with FastAPI updates.

    path_param_names = get_path_param_names(path)
    endpoint_signature = get_typed_signature(call)
    signature_params = endpoint_signature.parameters
    dependant = Dependant(
        call=call,
        name=name,
        path=path,
        security_scopes=security_scopes,
        use_cache=use_cache,
    )
    for param_name, param in signature_params.items():
        # (ORWYNN) Ignore orwynn's framework internal arguments
        if param_name.startswith("_fw_"):
            continue

        is_path_param = param_name in path_param_names
        type_annotation, depends, param_field = analyze_param(
            param_name=param_name,
            annotation=param.annotation,
            value=param.default,
            is_path_param=is_path_param,
        )
        if depends is not None:
            sub_dependant = get_param_sub_dependant(
                param_name=param_name,
                depends=depends,
                path=path,
                security_scopes=security_scopes,
            )
            dependant.dependencies.append(sub_dependant)
            continue
        if add_non_field_param_to_dependency(
            param_name=param_name,
            type_annotation=type_annotation,
            dependant=dependant,
        ):
            assert (  # noqa: S101
                    param_field is None
                ), \
                "Cannot specify multiple FastAPI annotations for" \
                + f" {param_name!r}"
            continue
        assert param_field is not None  # noqa: S101
        if is_body_param(param_field=param_field, is_path_param=is_path_param):
            dependant.body_params.append(param_field)
        else:
            add_param_to_fields(field=param_field, dependant=dependant)
    return dependant



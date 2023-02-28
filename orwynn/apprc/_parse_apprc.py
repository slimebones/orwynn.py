import contextlib
import os
from pathlib import Path
from types import NoneType

from orwynn.app import AppMode
from orwynn.apprc._AppRc import AppRc
from orwynn.util import validation
from orwynn.util.mp import patch as mp_patch
from orwynn.util.yml import load_yml

from ._APP_RC_MODE_NESTING import APP_RC_MODE_NESTING
from ._AppRcSearchError import AppRcSearchError


def parse_apprc(
    root_dir: Path,
    mode: AppMode,
    direct_apprc: AppRc | None
) -> AppRc:
    """Parses apprc dictionary.

    Args:
        root_dir:
            Root dir of app.
        mode:
            Boot mode of app.
        direct_apprc:
            AppRc raw configuration passed directly instead of path to it via
            environ. This arg is not optional and should accept None directly,
            if such apprc is not present to enable environ searching way.
    """
    validation.validate(root_dir, Path)
    validation.validate(mode, AppMode)
    validation.validate(direct_apprc, [AppRc, NoneType])

    # All required for this enabled mode data goes here
    final_apprc: AppRc = {}

    if not direct_apprc:
        rc_path_env: str = os.getenv(
            "Orwynn_AppRcPath",
            ""
        )
        should_raise_search_error: bool

        rc_path: Path
        if not rc_path_env:
            rc_path = Path(root_dir, "apprc.yml")
            # On default assignment no errors raised if files not found / empty
            should_raise_search_error = False
        else:
            # Env path started from "./" is supported in this case of
            # concatenation since pathlib.Path does smart path joining
            rc_path = Path(root_dir, rc_path_env)
            should_raise_search_error = True

        if Path(rc_path).exists():
            # Here goes all data contained in yaml config
            apprc: AppRc = load_yml(rc_path)
            __parse_into(final_apprc, apprc, should_raise_search_error, mode)
        elif (
            rc_path_env.startswith("http://")
            or rc_path_env.startswith("https://")
        ):
            raise NotImplementedError("URL sources are not yet implemented")

        elif should_raise_search_error:
            raise AppRcSearchError(
                f"unsupported apprc path {rc_path}"
            )
    else:
        # For direct app rc emptiness check should be always performed, so we
        # pass True
        __parse_into(final_apprc, direct_apprc, True, mode)

    return final_apprc


def __parse_into(
    receiver: dict,
    source: dict,
    should_check_if_source_empty: bool,
    mode: AppMode
) -> None:
    if source == {} and should_check_if_source_empty:
        raise ValueError("parsed apprc source is empty")

    # Check if apprc contains any unsupported top-level keys
    for k in receiver:
        supported_top_level_keys: list[str] = [
            x.value for x in AppMode
        ]
        if k not in supported_top_level_keys:
            raise ValueError(
                f"unsupported top-level key \"{k}\" of apprc config"
            )

    # Load from bottom to top updating previous one with newest one
    mode_nesting_index: int = APP_RC_MODE_NESTING.index(mode)
    for nesting_mode in APP_RC_MODE_NESTING[:mode_nesting_index + 1]:
        # Supress: We don't mind if any top-level key is missing here
        with contextlib.suppress(KeyError):
            mp_patch(
                receiver,
                source[nesting_mode.value],
                should_deepcopy=False
            )

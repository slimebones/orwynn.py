import contextlib
import os
from pathlib import Path
from types import NoneType
from orwynn import mp, validation
from orwynn.apprc.APP_RC_MODE_NESTING import APP_RC_MODE_NESTING
from orwynn.apprc.AppRC import AppRC
from orwynn.apprc.AppRCSearchError import AppRCSearchError
from orwynn.boot.BootMode import BootMode
from orwynn.file.yml import load_yml
from orwynn.mp import dictpp


def parse_apprc(
    root_dir: Path,
    mode: BootMode,
    direct_apprc: AppRC | None
) -> AppRC:
    """Parses apprc dictionary.

    Args:
        root_dir:
            Root dir of app.
        mode:
            Boot mode of app.
        direct_apprc:
            AppRC raw configuration passed directly instead of path to it via
            environ. This arg is not optional and should accept None directly,
            if such apprc is not present to enable environ searching way.
    """
    validation.validate(root_dir, Path)
    validation.validate(mode, BootMode)
    validation.validate(direct_apprc, [AppRC, NoneType])

    # All required for this enabled mode data goes here
    final_apprc: AppRC = dictpp()

    if not direct_apprc:
        rc_path_env: str = os.getenv(
            "Orwynn_AppRCPath",
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
            apprc: AppRC = dictpp(load_yml(rc_path))
            __parse_into(final_apprc, apprc, should_raise_search_error, mode)

        elif (
            rc_path_env.startswith("http://")
            or rc_path_env.startswith("https://")
        ):
            raise NotImplementedError("URL sources are not yet implemented")

        elif should_raise_search_error:
            raise AppRCSearchError(
                f"unsupported apprc path {rc_path}"
            )
    else:
        # For direct app rc empty check should be always performed, so we pass
        # True
        __parse_into(final_apprc, direct_apprc, True, mode)

    return final_apprc


def __parse_into(
    receiver: dictpp,
    source: dictpp,
    should_check_if_source_empty: bool,
    mode: BootMode
) -> None:
    if source == {} and should_check_if_source_empty:
        raise ValueError(f"parsed apprc source is empty")

    # Check if apprc contains any unsupported top-level keys
    for k in receiver.keys():
        supported_top_level_keys: list[str] = [
            x.value for x in BootMode
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
            mp.patch(
                receiver,
                source[nesting_mode.value],
                should_deepcopy=False
            )

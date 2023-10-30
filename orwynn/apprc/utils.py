import contextlib
import os
from pathlib import Path
from types import NoneType

from antievil import NotFoundError

from orwynn.app import AppMode
from orwynn.apprc.apprc import AppRc
from orwynn.utils import validation
from orwynn.utils.klass import Static
from orwynn.utils.mp import patch as mp_patch
from orwynn.utils.yml import load_yml

from .constants import APP_RC_MODE_NESTING


class AppRCUtils(Static):
    @staticmethod
    def parse(
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
                AppRc raw configuration passed directly instead of path to it
                via environ. This arg is not optional and should accept None
                directly, if such apprc is not present to enable environ
                searching way.
        """
        validation.validate(root_dir, Path)
        validation.validate(mode, AppMode)
        validation.validate(direct_apprc, [AppRc, NoneType])

        # All required for this enabled mode data goes here
        final_apprc: AppRc = {}

        if not direct_apprc:
            rc_paths: list[Path] = [
                Path(root_dir, "orwynn.yml"),
            ]

            env_path: str | None = os.getenv("ORWYNN_RC_PATH", None)
            if env_path is not None:
                final_path: Path = Path(root_dir, env_path)
                if not final_path.exists():
                    raise NotFoundError(
                        title="specified in environ path",
                        value=final_path
                    )
                # look only for environ path
                rc_paths = [final_path]

            for p in rc_paths:
                if p.exists():
                    # Here goes all data contained in yaml config
                    apprc: AppRc = load_yml(p)
                    AppRCUtils._parse_into(
                        final_apprc, apprc, False, mode
                    )
                    break
        else:
            # For direct app rc emptiness check should be always performed, so
            # we pass True
            AppRCUtils._parse_into(final_apprc, direct_apprc, True, mode)

        return final_apprc

    @staticmethod
    def _parse_into(
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

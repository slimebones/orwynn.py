from pykit.env import getenv_bool, getenv


class OrwynnEnvUtils:
    @classmethod
    def is_debug(cls) -> bool:
        return getenv_bool(key="ORWYNN_DEBUG", default="0").eject()

    @classmethod
    def is_clean_allowed(cls) -> bool:
        return getenv_bool(
            key="ORWYNN_ALLOW_CLEAN",
            default="0").eject()

    @classmethod
    def get_mode(cls) -> str:
        return getenv(key="ORWYNN_MODE", default="__default__").eject()

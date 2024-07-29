from pykit.env import getenv, getenv_bool


def is_debug() -> bool:
    return getenv_bool(key="ORWYNN_DEBUG", default="0").eject()

def is_clean_allowed() -> bool:
    return getenv_bool(
        key="ORWYNN_ALLOW_CLEAN",
        default="0").eject()

def get_mode() -> str:
    return getenv(key="ORWYNN_MODE", default="__default__").eject()

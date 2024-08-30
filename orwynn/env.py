from ryz.env import getenv


def is_debug() -> bool:
    return getenv("ORWYNN_DEBUG", "0").unwrap() == "1"

def is_clean_allowed() -> bool:
    return getenv("ORWYNN_ALLOW_CLEAN", "0").unwrap() == "1"

def get_mode() -> str:
    return getenv(key="ORWYNN_MODE", default="__default__").unwrap()

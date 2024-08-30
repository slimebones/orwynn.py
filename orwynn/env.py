from ryz import env


def is_debug() -> bool:
    return env.get("ORWYNN_DEBUG", "0").unwrap() == "1"

def is_clean_allowed() -> bool:
    return env.get("ORWYNN_ALLOW_CLEAN", "0").unwrap() == "1"

def get_mode() -> str:
    return env.get(key="ORWYNN_MODE", default="__default__").unwrap()

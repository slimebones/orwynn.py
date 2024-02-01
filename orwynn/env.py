from pykit.env import EnvSpec, EnvUtils


class OrwynnEnvUtils:
    @classmethod
    def is_debug(cls) -> bool:
        return EnvUtils.get_bool(EnvSpec(key="ORWYNN_DEBUG", default="0"))

    @classmethod
    def is_clean_allowed(cls) -> bool:
        return EnvUtils.get_bool(EnvSpec(
            key="ORWYNN_ALLOW_CLEAN",
            default="0"
        ))

    @classmethod
    def get_mode(cls) -> str:
        env = EnvUtils.get(EnvSpec(key="ORWYNN_MODE", default="__default__"))
        return env

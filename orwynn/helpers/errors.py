from antievil import UnsupportedError

__all__ = [
    "UnsupportedError"
]

class DeprecatedFeatureError(Exception):
    """
    Feature is deprecated.
    """
    def __init__(
        self,
        *,
        deprecated_feature: str,
        use_instead: str
    ):
        message: str = \
            f"feature <{deprecated_feature}> is deprecated," \
            f" use {use_instead} instead"
        super().__init__(message)

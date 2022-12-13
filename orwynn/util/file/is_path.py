from pathlib import PosixPath, WindowsPath
from typing import Any


def is_path(p: Any) -> bool:
    """Checks if is an any kind of pathlib.Path.

    Args:
        p:
            Path to check.

    Returns:
        Positive/Negative result of check.
    """
    return type(p) in [PosixPath, WindowsPath]

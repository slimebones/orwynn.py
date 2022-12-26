import io
from contextlib import redirect_stdout
from typing import Callable


def capture_stdout(fn: Callable, *args, **kwargs) -> str:
    """Take stdout of given function call."""
    stringio = io.StringIO()
    with redirect_stdout(stringio):
        fn(*args, **kwargs)
    return stringio.getvalue()

from contextlib import contextmanager
from contextvars import Token
from typing import Optional
from orwynn import validation
from orwynn.web.context.ContextStorage import ContextStorage


@contextmanager
def context_manager(
    data: Optional[dict] = None
):
    """Populates the context storage with the given data.

    Args:
        data (optional):
            Dict to populate the created storage with. Defaults to empty dict.
    """
    if data is None:
        data = {}

    validation.validate(data, dict)

    storage: ContextStorage = ContextStorage.ie()
    token: Token = storage.init_data(data)

    try:
        yield
    finally:
        storage.reset(token)

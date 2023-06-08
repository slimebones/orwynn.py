from contextlib import contextmanager
from contextvars import Token

from orwynn.context.storage import ContextStorage
from orwynn.utils import validation


@contextmanager
def context_manager(
    data: dict | None = None
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

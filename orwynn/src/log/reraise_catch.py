import contextlib

from orwynn.src.log.Log import Log


def reraise_catch(error: Exception):
    """Reraise error and catch it by logger."""
    # TODO: Find way to remove this last function from exception stack to not
    #   be displayed

    # try-except block for correct linting even if error isn't actually passed
    # up the stack
    with contextlib.suppress(Exception), Log.catch(reraise=False):
        raise error

import contextlib

from orwynn.log.log import Log


def catch_error(error: Exception):
    """Reraise error and catch it by logger."""
    # TODO: Find way to remove this last function from exception stack to not
    #   be displayed

    # try-except block for correct linting even if error isn't actually passed
    # up the stack
    with contextlib.suppress(Exception), Log.catch(reraise=False):
        raise error


catchr = Log.catch(reraise=True)
"""
Shortcut for Log.catch(reraise=True).

Does not accept additional arguments.
"""

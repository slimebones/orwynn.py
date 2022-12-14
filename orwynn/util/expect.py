from typing import Callable


class ExpectationError(Exception):
    pass


def expect(
    fn: Callable,
    ErrorToExpect: type[Exception],
    *args,
    **kwargs
) -> None:
    """Expects given function to raise given error if function is called with
    given args and kwargs.

    Args:
        fn:
            Function to call.
        ErrorToExpect:
            Exception class to expect.
        args:
            Positional arguments to pass to function call.
        kwargs:
            Keyword arguments to pass to function call.

    Raises:
        ExpectationError:
            Given error has not been raised on function's call.
    """
    try:
        fn(*args, **kwargs)
    except ErrorToExpect:
        pass
    else:
        raise ExpectationError(
            f"{ErrorToExpect} expected on call of function {fn}"
        )

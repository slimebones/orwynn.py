from collections.abc import Callable
from typing import Any

from orwynn.base import Model


class FuncSpec(Model):
    """
    Holds information about some function.
    """
    fn: Callable
    args: tuple | None = None
    kwargs: dict | None = None

    def call(
        self,
        *,
        prepended_extra_args: tuple | None = None,
        appended_extra_args: tuple | None = None,
        prepended_extra_kwargs: dict | None = None,
        appended_extra_kwargs: dict | None = None,
    ) -> Any:
        """
        Calls a specified in this spec function.
        """
        args: tuple = ()
        if self.args is not None:
            args = self.args

        kwargs: dict = {}
        if self.kwargs is not None:
            kwargs = self.kwargs

        if prepended_extra_args is None:
            prepended_extra_args = ()
        if appended_extra_args is None:
            appended_extra_args = ()
        if prepended_extra_kwargs is None:
            prepended_extra_kwargs = {}
        if appended_extra_kwargs is None:
            appended_extra_kwargs = {}

        final_args: tuple = prepended_extra_args + args + appended_extra_args
        final_kwargs: dict = {
            **prepended_extra_kwargs,
            **kwargs,
            **appended_extra_kwargs,
        }

        return self.fn(*final_args, **final_kwargs)

from pprint import pprint
from typing import Callable
from pydantic import validate_arguments
from sqlalchemy import inspect
from orwynn import validation

from orwynn.error.catching.DEFAULT_EXCEPTION_HANDLERS import DEFAULT_EXCEPTION_HANDLERS
from orwynn.error.catching.ExceptionHandler import ExceptionHandler
from orwynn.error.catching.ExceptionAlreadyHandledError import \
    ExceptionAlreadyHandledError
from orwynn.error.Error import Error
from orwynn.error.MalfunctionError import MalfunctionError
from orwynn.web.Protocol import Protocol


class ExceptionHandlerManager:
    """
    Controls the error flow setup for the system.

    Attributes:
        register_by_protocol:
            Dictionary of register functions for each protocol.
    """
    def get_populated_handlers_by_protocol(
        self,
        exception_handlers: set[ExceptionHandler]
    ) -> dict[Protocol, set[ExceptionHandler]]:
        """
        Forms a set of handlers populated with default ones if required.

        Args:
            exception_handlers:
                Set of error handlers to register.

        Returns:
            Populated set of exception handlers by their protocol.
        """
        handlers_by_protocol: dict[Protocol, set[ExceptionHandler]] = {}

        # Populate and register handlers separately for each protocol
        for protocol in Protocol:
            populated_handlers: set[ExceptionHandler] = \
                self.__populate_handlers(
                    self.__get_handlers_for_protocol(
                        protocol,
                        exception_handlers
                    )
                )

            if protocol in handlers_by_protocol:
                raise ValueError(
                    f"protocol {protocol} handled twice"
                )
            handlers_by_protocol[protocol] = populated_handlers

        return handlers_by_protocol

    def __get_handlers_for_protocol(
        self,
        protocol: Protocol,
        error_handlers: set[ExceptionHandler]
    ) -> set[ExceptionHandler]:
        """
        Collects all handlers for the given protocol.
        """
        final_set: set[ExceptionHandler] = set()

        for eh in error_handlers:
            if eh.PROTOCOL is protocol:
                final_set.add(eh)

        return final_set

    def __populate_handlers(
        self,
        error_handlers: set[ExceptionHandler]
    ) -> set[ExceptionHandler]:
        """
        Traverses handlers to find handled Python-builtin exceptions and the
        Orwynn's default Error.

        Returns:
            Set of populated handlers.
        """
        populated_handlers: set[ExceptionHandler] = set()
        __HandledExceptions: set[type[Exception]] = set()

        for eh in error_handlers:
            if eh.E is None:
                raise MalfunctionError(
                    f"handler {eh} attribute E cannot be None"
                )
            else:
                if eh.E in __HandledExceptions:
                    raise ExceptionAlreadyHandledError(
                        f"exception {eh.E} is already handled"
                    )
                elif (
                    issubclass(eh.E, Exception)
                    and not issubclass(eh.E, Error)
                ):
                    __HandledExceptions.add(eh.E)
                elif issubclass(eh.E, Error):
                    __HandledExceptions.add(eh.E)
                else:
                    raise MalfunctionError(
                        f"unrecognized error {eh.E}"
                    )

            populated_handlers.add(eh)

        # Add default handlers for errors for which the custom's handlers were
        # not added
        for GenericDefaultErrorHandler in DEFAULT_EXCEPTION_HANDLERS:
            if GenericDefaultErrorHandler.E not in __HandledExceptions:
                populated_handlers.add(
                    GenericDefaultErrorHandler()
                )

        return populated_handlers

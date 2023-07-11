from orwynn.base.error.errors import (ExceptionAlreadyHandledError,
                                      MalfunctionError)
from orwynn.base.errorhandler import ErrorHandler
from orwynn.http import DEFAULT_HTTP_ERROR_HANDLERS
from orwynn.utils.scheme import Scheme
from orwynn.websocket import DEFAULT_WEBSOCKET_EXCEPTION_HANDLERS


class ErrorHandlerManager:
    """
    Controls the error flow setup for the system.

    Attributes:
        register_by_protocol:
            Dictionary of register functions for each protocol.
    """
    def get_populated_handlers_by_protocol(
        self,
        exception_handlers: set[ErrorHandler]
    ) -> dict[Scheme, set[ErrorHandler]]:
        """
        Forms a set of handlers populated with default ones if required.

        Args:
            exception_handlers:
                Set of error handlers to register.

        Returns:
            Populated set of exception handlers by their protocol.
        """
        handlers_by_protocol: dict[Scheme, set[ErrorHandler]] = {}

        # Populate and register handlers separately for each protocol
        for scheme in Scheme:
            if scheme is not Scheme.HTTP and scheme is not Scheme.WEBSOCKET:
                continue

            populated_handlers: set[ErrorHandler] = \
                self.__populate_handlers(
                    self.__get_handlers_for_protocol(
                        scheme,
                        exception_handlers
                    ),
                    scheme
                )

            if scheme in handlers_by_protocol:
                raise ValueError(
                    f"protocol {scheme} handled twice"
                )
            handlers_by_protocol[scheme] = populated_handlers

        return handlers_by_protocol

    def __get_handlers_for_protocol(
        self,
        protocol: Scheme,
        error_handlers: set[ErrorHandler]
    ) -> set[ErrorHandler]:
        """
        Collects all handlers for the given protocol.
        """
        final_set: set[ErrorHandler] = set()

        for eh in error_handlers:
            if eh.PROTOCOL is protocol:
                final_set.add(eh)

        return final_set

    def __populate_handlers(
        self,
        error_handlers: set[ErrorHandler],
        protocol: Scheme
    ) -> set[ErrorHandler]:
        """
        Traverses handlers to find handled Python-builtin exceptions.

        Returns:
            Set of populated handlers.
        """
        populated_handlers: set[ErrorHandler] = set()
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
                elif issubclass(eh.E, Exception):
                    __HandledExceptions.add(eh.E)
                else:
                    raise MalfunctionError(
                        f"unrecognized error {eh.E}"
                    )

            populated_handlers.add(eh)

        # Add default handlers for errors for which the custom's handlers were
        # not added
        DEFAULT_HANDLERS: set[type[ErrorHandler]]
        match protocol:
            case Scheme.HTTP:
                DEFAULT_HANDLERS = DEFAULT_HTTP_ERROR_HANDLERS
            case Scheme.WEBSOCKET:
                DEFAULT_HANDLERS = DEFAULT_WEBSOCKET_EXCEPTION_HANDLERS
            case _:
                raise TypeError(
                    f"unrecognized protocol {protocol}"
                )

        for GenericDefaultErrorHandler in DEFAULT_HANDLERS:
            if GenericDefaultErrorHandler.E not in __HandledExceptions:
                populated_handlers.add(
                    GenericDefaultErrorHandler()
                )

        return populated_handlers

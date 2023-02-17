from pprint import pprint
from pydantic import validate_arguments
from sqlalchemy import inspect
from orwynn import validation

from orwynn.error.catching.DEFAULT_ERROR_HANDLERS import DEFAULT_ERROR_HANDLERS
from orwynn.error.catching.ErrorHandler import ErrorHandler
from orwynn.error.catching.ErrorHandlerBuiltinHttpMiddleware import \
    ErrorHandlerBuiltinHttpMiddleware
from orwynn.error.catching.ErrorHandlerBuiltinWebsocketMiddleware import \
    ErrorHandlerBuiltinWebsocketMiddleware
from orwynn.error.catching.ExceptionAlreadyHandledError import \
    ExceptionAlreadyHandledError
from orwynn.error.Error import Error
from orwynn.error.MalfunctionError import MalfunctionError
from orwynn.middleware.Middleware import Middleware
from orwynn.web.Protocol import Protocol


class ErrorHandlerManager:
    """
    Controls the error flow setup for the system.

    Attributes:
        handler_register:
            A function to regsiter new handlers.
    """
    def __init__(self) -> None:
        # Contains all handled exceptions in the system
        self.__HandledExceptions: list[type[Exception]] = []
        self.__middleware_by_handler: dict[
            ErrorHandler, Middleware
        ] = {}

    def get_middleware_from_handlers(
        self,
        error_handlers: list[ErrorHandler]
    ) -> list[Middleware]:
        """
        Traverses all error handlers to create according catching middleware
        for them.

        Args:
            error_handlers:
                List of error handlers to add.

        Returns:
            List of error catch middleware.
        """
        self.__collect_middleware(
            self.__populate_handlers(error_handlers)
        )

        return self.__arrange_middleware()

    def __populate_handlers(
        self,
        error_handlers: list[ErrorHandler]
    ) -> list[ErrorHandler]:
        """
        Traverses handlers to find handled Python-builtin exceptions and the
        Orwynn's default Error.

        Returns:
            Fully collected error handlers.
        """
        populated_handlers: list[ErrorHandler] = []

        # NOTE: Separation by two variables each for builtin and framework
        # errors is made for better future arrangement speed, since builtin
        # exceptions are always can be considered as having less detail level
        # (or placed independently) in terms of handling.
        HandledBuiltinExceptions: list[type[Exception]] = []
        HandledErrors: list[type[Error]] = []

        is_default_error_handled: bool = False

        for eh in error_handlers:
            if eh.E is None:
                raise MalfunctionError(
                    f"handler {eh} attribute E cannot be None"
                )
            else:
                if eh.E in HandledBuiltinExceptions + HandledErrors:
                    raise ExceptionAlreadyHandledError(
                        f"exception {eh.E} is already handled"
                    )
                elif (
                    issubclass(eh.E, Exception)
                    and not issubclass(eh.E, Error)
                ):
                    HandledBuiltinExceptions.append(eh.E)
                elif issubclass(eh.E, Error):
                    if eh.E is Error:
                        is_default_error_handled = True
                    HandledErrors.append(eh.E)
                else:
                    raise MalfunctionError(
                        f"unrecognized error {eh.E}"
                    )

        # Add builtin exceptions for future arrangements to the final list
        self.__HandledExceptions += HandledBuiltinExceptions
        # And then add framework errors, adding it only after Python-builtin
        # exceptions might decrease latter error's rearrangement by detail time
        self.__HandledExceptions += HandledErrors

        # FIXME: Here below the default exception handlers are created without
        #   the Di notifying which may raise a confusion in the next calls.

        # Add default handlers for errors for which the custom's handlers were
        # not added
        for GenericDefaultErrorHandler in DEFAULT_ERROR_HANDLERS:
            if GenericDefaultErrorHandler.E not in self.__HandledExceptions:
                populated_handlers.append(GenericDefaultErrorHandler())
                self.__HandledExceptions.append(
                    GenericDefaultErrorHandler.get_handled_exception_class()
                )

        return populated_handlers

    def __collect_middleware(
        self,
        error_handlers: list[ErrorHandler]
    ) -> list[Middleware]:
        """
        Instantiates a middleware for each error handler.

        Returns:
            A list of created middleware.
        """
        middleware_list: list[Middleware] = []

        middleware: Middleware
        for eh in error_handlers:
            match eh.PROTOCOL:
                case Protocol.HTTP:
                    middleware = ErrorHandlerBuiltinHttpMiddleware(
                        handler=eh
                    )
                case Protocol.WEBSOCKET:
                    middleware = ErrorHandlerBuiltinWebsocketMiddleware(
                        handler=eh
                    )
                case _:
                    raise TypeError(
                        f"unrecognized error handler {eh} protocol"
                        f" {eh.PROTOCOL}"
                    )

            if type(eh) in [type(eh_) for eh_ in self.__middleware_by_handler]:
                raise ValueError(
                    f"type of error handler {eh} has been already registered"
                )
            self.__middleware_by_handler[eh] = middleware

            middleware_list.append(
                middleware
            )

        return middleware_list

    def __arrange_middleware(
        self
    ) -> list[Middleware]:
        """
        Returns a new list with middleware with a less detailed error handled
        first.
        """
        rearranged: list[type[Exception]] = \
            self.__HandledExceptions.copy()

        # Sort more detailed to the start of the list
        length: int = len(rearranged)
        for i in range(0, length):
            for j in range(i + 1, length):
                if self.__is_more_detailed(
                    rearranged[i],
                    rearranged[j]
                ):
                    rearranged[i], rearranged[j] = rearranged[j], rearranged[i]

        return [
            self.__find_middleware_by_exception(Exc)
            for Exc in rearranged
        ]

    def __find_middleware_by_exception(
        self,
        TargetException: type[Exception]
    ) -> Middleware:
        for eh, middleware in self.__middleware_by_handler.items():
            if eh.E is TargetException:
                return middleware

        raise ValueError(
            "no middleware registered for an exception class"
            f" {TargetException}"
        )

    def __is_more_detailed(
        self,
        Exception1: type[Exception],
        Exception2: type[Exception]
    ) -> bool:
        """
        Compares if the exception #1 is more detailed than the exception #2.

        Returns:
            True, if the exception #1 is more detailed than the exception #2
            and False otherwise. Also returns False if the given exceptions is
            on the same level of detail.
        """
        validation.validate(Exception1, Exception)
        validation.validate(Exception2, Exception)

        mro1: list[type] = Exception1.mro()

        if Exception2 in mro1:
            # Exception1 is inherited from Exception2, so it's de-facto more
            # detailed
            return True
        else:
            # All other cases lead to less or equal level of detail.
            return False

from orwynn.error.catching.ExceptionHandler import ExceptionHandler


HandlerByExceptionClass = dict[type[Exception], ExceptionHandler]

from orwynn.base.error import Error


class NotProviderError(Error):
    def __init__(
        self,
        message: str = "",
        FailedClass: type | None = None
    ) -> None:
        if not message and FailedClass:
            message = "{} is not a Provider".format(FailedClass)
        super().__init__(message)

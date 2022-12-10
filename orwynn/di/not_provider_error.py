from orwynn.base.error.error import Error


class NotProviderError(Error):
    def __init__(
        self,
        message: str = "",
        FailedClass: type | None = None
    ) -> None:
        if not message and FailedClass:
            message = "{} is not a provider".format(FailedClass)
        super().__init__(message)
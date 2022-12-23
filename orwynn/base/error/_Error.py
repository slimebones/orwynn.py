from orwynn.proxy.APIIndicationOnlyProxy import APIIndicationOnlyProxy


class Error(Exception):
    """Base error class of the app.

    Attributes:
        message (optional):
            Message to be attached to the error.
    """
    def __init__(self, message: str = "") -> None:
        super().__init__(message)
        self.message = message

    @property
    def api(self) -> dict:
        """Generates API-complying object using project's defined API
        indication.
        """
        return APIIndicationOnlyProxy.ie().api_indication.digest(self)

    def dict(self, *args, **kwargs) -> dict:
        return {"message": self.message}

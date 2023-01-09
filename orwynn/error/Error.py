from orwynn.proxy.APIIndicationOnlyProxy import APIIndicationOnlyProxy


class Error(Exception):
    """Base error class of the app.

    Attributes:
        message (optional):
            Message to be attached to the error.
        status_code (optional):
            Status code to be retrieved by error handlers.
    """
    def __init__(self, message: str = "", status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    @property
    def api(self) -> dict:
        """Generates API-complying object using project's defined API
        indication.
        """
        return APIIndicationOnlyProxy.ie().api_indication.digest(self)

    def dict(self, *args, **kwargs) -> dict:
        return {"message": self.message}

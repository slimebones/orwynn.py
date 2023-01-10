class HttpError(Exception):
    """Base error class of the app."""
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code

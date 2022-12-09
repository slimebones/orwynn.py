class Error(Exception):
    """Base error class of the app."""
    def __init__(self, message: str = "") -> None:
        super().__init__(message)
        self.message = message
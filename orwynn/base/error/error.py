class Error(Exception):
    """Base error class of the app.
    
    Attributes:
        message (optional):
            Message to be attached to the error.
    """
    def __init__(self, message: str = "") -> None:
        super().__init__(message)
        self.message = message
class BootError(Exception):
    """Occured at boottime."""
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
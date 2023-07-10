class InvalidAddressError(Exception):
    def __init__(
        self,
        *,
        address: str
    ):
        message: str = f"address <{address}> is invalid"
        super().__init__(message)

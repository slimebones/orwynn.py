class DtoError(Exception):
    """
    @abstract
    """


class HasCodeButNoAttributeDtoError(DtoError):
    """
    When a dto does not have `Code` attribute set, but got `code` field.
    """
    def __init__(
        self,
        *,
        code_field: str,
    ):
        message: str = \
            "dto does not have Code attribute but does have `code` field=" \
            f"{code_field}"
        super().__init__(message)


class UnmatchedCodeFieldDtoError(DtoError):
    """
    When dto's `code` field does not match Code class attribute.
    """
    def __init__(
        self,
        *,
        code_field: str,
        code_attribute: str,
    ):
        message: str = \
            f"explicitly given code field={code_field}" \
            f" does not match a class's defined attribute={code_attribute}"
        super().__init__(message)


class AbstractDtoClassAsBaseDtoError(DtoError):
    """
    Container cannot declare base dto class as BASE attribute.
    """
    def __init__(
        self,
    ):
        message: str = "container cannot declare abstract Dto class as BASE"
        super().__init__(message)

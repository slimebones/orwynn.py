from orwynn.utils.condition._mark import ComparisonMark


class UnsupportedComparisonError(Exception):
    """
    Objects of type does not support certain comparison.
    """
    def __init__(
        self,
        *,
        Type: type,
        compare_mark: ComparisonMark,
    ) -> None:
        message: str = \
            f"objects of type <{Type}> does not support" \
            f" comparison <{compare_mark}>"
        super().__init__(message)

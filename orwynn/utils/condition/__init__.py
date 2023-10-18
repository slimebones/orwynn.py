from typing import Any, Generic, TypeVar

from orwynn.utils.condition._mark import ComparisonMark
from orwynn.utils.condition.errors import UnsupportedComparisonError
from antievil import UnsupportedError, WrongGenericTypeError

T = TypeVar("T")


class ComparisonCondition(Generic[T]):
    """
    Contains condition mark and a value to compare to target.

    Attributes:
        mark:
            Compare mark relative to target. For example if the mark is set to
            MoreEqual, it means that the target should be more or equal than
            the value given to this condition, i.e.
            target >= ComparisonCondition.value.
        value:
            Value to compare to. Should be Comparable and contain all methods
            of comparison to satisfy ComparisonMark fields (aka python dunder
            comparators like `__le__`).
    """

    # TODO(ryzhovalex): ensure that operated value and target type
    #   can handle the chosen mark's comparison (i.e. has an according dunder
    #   comparator method)
    # 0

    def __init__(self, mark: ComparisonMark, value: T) -> None:
        self._mark: ComparisonMark = mark
        self._value: T = value

    def __str__(self) -> str:
        return f"\"{self.mark.value}\" {self.value}"

    @property
    def mark(self) -> ComparisonMark:
        return self._mark

    @property
    def value(self) -> T:
        return self._value

    def compare(self, target: T) -> bool:
        """
        Compares given target to the condition's value using condition's
        defined compare mark.

        Args:
            target:
                Target to compare.

        Returns:
            Comparison result as a boolean.

        Raises:
            UnsupportedComparisonError:
                Type of target and value does not support chosen comparison.
            WrongGenericTypeError:
                Target's type is different from condition's value type.
            UnsupportedError:
                Unrecognized compare mark defined by condition.
        """
        self._check_target_type(target)

        try:
            return self._compare(target)
        except TypeError as error:
            raise UnsupportedComparisonError(
                Type=type(target),
                compare_mark=self._mark,
            ) from error

    def _compare(
        self,
        target: T,
    ) -> bool:
        match self._mark:
            case ComparisonMark.Equal:
                return target == self._value
            case ComparisonMark.NotEqual:
                return target != self._value
            # ignore linter comparison errors since we handle it at
            # runtime
            case ComparisonMark.More:
                return target > self._value  # type: ignore
            case ComparisonMark.Less:
                return target < self._value  # type: ignore
            case ComparisonMark.MoreEqual:
                return target >= self._value  # type: ignore
            case ComparisonMark.LessEqual:
                return target <= self._value  # type: ignore
            case _:
                raise UnsupportedError(
                    title="compare mark",
                    value=self._mark,
                )

    def _check_target_type(self, target: T) -> None:
        if type(target) is not type(self._value):
            raise WrongGenericTypeError(
                GenericClass=type(self),
                ExpectedType=type(self._value),
                ReceivedType=type(target),
            )

from typing import Any, ClassVar, Generic

from antievil import AbstractUsageError
from pydantic.generics import GenericModel

from orwynn.utils.condition import ComparisonCondition as _ComparisonCondition
from orwynn.utils.expectation.errors import (
    ExpectationError,
    UnsupportedExpectationTypeError,
)
from orwynn.utils.types import T


class Expectation(GenericModel, Generic[T]):
    """
    Parameter-model signifies which checks should be performed.

    All expectations are based on return type. E.g. if your function returns
    a List, you should consider using ListExpectation.

    All expectations can be checked via general function `self.check()`.

    Class-attributes:
        SUPPPORTED_TYPES(optional):
            Which types the expectation supports. Defaults to None, but only
            for abstract classes.

    @abstract
    """
    SUPPORTED_TYPES: ClassVar[list[type] | None] = None

    @classmethod
    def is_supported(cls, Type: type[T]) -> bool:
        """
        Checks whether the given type is supported by the class.
        """
        if cls.SUPPORTED_TYPES is None:
            raise AbstractUsageError(
                explanation="cannot check supported types",
                Class=cls,
            )
        else:
            return Type in cls.SUPPORTED_TYPES

    def check(
        self,
        target: T,
    ) -> None:
        """
        Checks expectation against the given target.

        Args:
            target:
                Target to check.

        Raises:
            UnsupportedExpectationTypeError:
                The type of given target is not supported by the expectation.
            ExpectationError:
                Any of expectation checks against the target has been failed.
        """
        self._check_target_type(target)
        self._check(target)

    def _check(self, target: T):
        """
        Main check function. Should be redefined at children.
        """
        raise AbstractUsageError(
            explanation="cannot call check function",
            Class=type(self),
        )

    def _check_target_type(self, target: T) -> None:
        if not self.is_supported(type(target)):
            raise UnsupportedExpectationTypeError(
                UnsupportedType=type(target),
                expectation=self,
            )

    class Config:
        arbitrary_types_allowed = True


class ListExpectation(Expectation[T], Generic[T]):
    """
    Expectation rules for List return type.

    Attributes:
        count(optional):
            Condition signifies how many items should the list contain.
    """
    SUPPORTED_TYPES = [list]

    count: _ComparisonCondition[int] | None = None

    def _check(self, target: list[T]):
        if self.count is not None and not self.count.compare(len(target)):
            raise ExpectationError(
                title="count",
                actual_value=len(target),
                expected_value=self.count,
            )

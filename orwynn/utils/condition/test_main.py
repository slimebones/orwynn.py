from antievil import WrongGenericTypeError

from orwynn.utils import validation
from orwynn.utils.condition import ComparisonCondition
from orwynn.utils.condition._mark import ComparisonMark
from orwynn.utils.condition.errors import UnsupportedComparisonError


def test_int_equal():
    condition: ComparisonCondition[int] = ComparisonCondition(
        ComparisonMark.Equal,
        value=5,
    )

    assert condition.compare(5)
    assert not condition.compare(10)


def test_int_wrong_type():
    condition: ComparisonCondition[int] = ComparisonCondition(
        ComparisonMark.Equal,
        value=5,
    )

    validation.expect(
        condition.compare,
        WrongGenericTypeError,
        "impostor",
    )


def test_int_less_equal():
    condition: ComparisonCondition[int] = ComparisonCondition(
        ComparisonMark.LessEqual,
        value=5,
    )

    assert condition.compare(1)
    assert condition.compare(5)
    assert not condition.compare(10)


def test_unsupported_comparison():
    condition: ComparisonCondition[dict[str, int]] = ComparisonCondition(
        ComparisonMark.LessEqual,
        value={"hello": 1},
    )

    validation.expect(
        condition.compare,
        UnsupportedComparisonError,
        {
            "world": 2,
        },
    )

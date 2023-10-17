from orwynn.utils.condition import ComparisonCondition, ComparisonMark
from orwynn.utils.expectation import ListExpectation

one_item_list_expectation: ListExpectation = ListExpectation(
    count=ComparisonCondition(
        mark=ComparisonMark.Equal,
        value=1,
    ),
)

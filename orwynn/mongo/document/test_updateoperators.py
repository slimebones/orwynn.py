from orwynn.mongo.document.errors import InvalidOperatorError
from orwynn.mongo.document.testing import SimpleDocument
from orwynn.utils import validation


def test_min(document_1: SimpleDocument):
    document_1 = document_1.update(
        operators={
            "$min": {
                # less than specified
                "price": 0.5
            }
        }
    )

    assert document_1.price == 0.5


def test_min_fail(document_1: SimpleDocument):
    document_1 = document_1.update(
        operators={
            "$min": {
                # more than specified
                "price": 1.5
            }
        }
    )

    # the same amount should remain
    assert document_1.price == 1.2


def test_set_in_operators(document_1: SimpleDocument):
    """
    $set shouldn't appear in `operators` argument.
    """
    validation.expect(
        document_1.update,
        InvalidOperatorError,
        operators={
            "$set": {
                "price": 5
            }
        }
    )


def test_inc_in_operators(document_1: SimpleDocument):
    """
    $inc shouldn't appear in `operators` argument.
    """
    validation.expect(
        document_1.update,
        InvalidOperatorError,
        operators={
            "$inc": {
                "price": 5
            }
        }
    )

from tests.mongo.conftest import SimpleDocument


def test_min(document_1: SimpleDocument):
    f = document_1.try_upd(
        {
            "$min": {
                # less than specified
                "price": 0.5
            }
        }
    )
    assert f
    assert f.price == 0.5

def test_min_fail(document_1: SimpleDocument):
    f = document_1.try_upd(
        {
            "$min": {
                # more than specified
                "price": 1.5
            }
        }
    )
    assert f
    # the same amount should remain
    assert f.price == 1.2

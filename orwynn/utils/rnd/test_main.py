from orwynn.utils.rnd import makeid


def test_makeid():
    assert type(makeid()) is str

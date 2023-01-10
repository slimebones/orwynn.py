from orwynn.rnd import makeid


def test_makeid():
    assert type(makeid()) is str

from orwynn.util.rnd import makeid


def test_makeid():
    assert type(makeid()) is str

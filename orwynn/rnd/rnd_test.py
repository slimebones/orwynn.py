from orwynn.rnd import gen_uuid


def test_makeid():
    assert type(gen_uuid()) is str

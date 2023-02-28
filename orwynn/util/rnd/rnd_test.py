from orwynn.util.rnd import gen_id


def test_makeid():
    assert type(gen_id()) is str

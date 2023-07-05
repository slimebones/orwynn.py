from orwynn.mapping.errors import UnsetIdMappingError
from orwynn.utils import validation

from .mapping import Mapping


class _M1(Mapping):
    number: int


def test_try_set_id():
    m: Mapping = _M1(id="helloworld", number=1)

    assert m.id == "helloworld"


def test_get_id():
    m: Mapping = _M1(id="helloworld", number=2)

    assert m.getid() == "helloworld"


def test_get_id_unset():
    m: Mapping = _M1(number=2)

    validation.expect(
        m.getid,
        UnsetIdMappingError
    )

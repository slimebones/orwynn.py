from ._get_vars import get_vars
from ._UrlVars import UrlVars
from ._Url import Url


def test_path():
    vars: UrlVars = get_vars(
        url=Url("/user/eg1"),
        original_route="/user/{user_id}"
    )
    assert vars.path_vars["user_id"] == "eg1"
    assert vars.query_vars == {}


def test_path_2():
    vars: UrlVars = get_vars(
        url=Url("/user/eg1/hello"),
        original_route="/user/{user_id}/{user_sign}"
    )
    assert vars.path_vars["user_id"] == "eg1"
    assert vars.path_vars["user_sign"] == "hello"
    assert vars.query_vars == {}


def test_query():
    vars: UrlVars = get_vars(
        url=Url("/user?token=woo"),
        original_route="/user"
    )
    assert vars.path_vars == {}
    assert vars.query_vars["token"] == "woo"


def test_query_2():
    vars: UrlVars = get_vars(
        url=Url("/user?token=woo&order=5"),
        original_route="/user"
    )
    assert vars.path_vars == {}
    assert vars.query_vars["token"] == "woo"
    assert vars.query_vars["order"] == "5"


def test_mixed():
    vars: UrlVars = get_vars(
        url=Url("/user/eg1/hello?token=woo&order=5"),
        original_route="/user/{user_id}/{user_sign}"
    )
    assert vars.path_vars["user_id"] == "eg1"
    assert vars.path_vars["user_sign"] == "hello"
    assert vars.query_vars["token"] == "woo"
    assert vars.query_vars["order"] == "5"

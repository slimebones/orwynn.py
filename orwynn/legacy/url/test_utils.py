from orwynn.url import URL, URLUtils, URLVars


def test_path():
    vars: URLVars = URLUtils.get_vars(
        url=URL("/user/eg1"),
        abstract_route="/user/{user_id}"
    )
    assert vars.path_vars["user_id"] == "eg1"
    assert vars.query_vars == {}


def test_path_2():
    vars: URLVars = URLUtils.get_vars(
        url=URL("/user/eg1/hello"),
        abstract_route="/user/{user_id}/{user_sign}"
    )
    assert vars.path_vars["user_id"] == "eg1"
    assert vars.path_vars["user_sign"] == "hello"
    assert vars.query_vars == {}


def test_query():
    vars: URLVars = URLUtils.get_vars(
        url=URL("/user?token=woo"),
        abstract_route="/user"
    )
    assert vars.path_vars == {}
    assert vars.query_vars["token"] == "woo"


def test_query_2():
    vars: URLVars = URLUtils.get_vars(
        url=URL("/user?token=woo&order=5"),
        abstract_route="/user"
    )
    assert vars.path_vars == {}
    assert vars.query_vars["token"] == "woo"
    assert vars.query_vars["order"] == "5"


def test_mixed():
    vars: URLVars = URLUtils.get_vars(
        url=URL("/user/eg1/hello?token=woo&order=5"),
        abstract_route="/user/{user_id}/{user_sign}"
    )
    assert vars.path_vars["user_id"] == "eg1"
    assert vars.path_vars["user_sign"] == "hello"
    assert vars.query_vars["token"] == "woo"
    assert vars.query_vars["order"] == "5"

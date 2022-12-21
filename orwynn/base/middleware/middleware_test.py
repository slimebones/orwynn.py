from orwynn.base.test.HttpClient import HttpClient


def test_tmp(run_std_boot, std_http: HttpClient):
    std_http.get_jsonify("/text")
    assert False

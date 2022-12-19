from orwynn.base.module.Module import Module
from orwynn.base.test.HttpClient import HttpClient
from orwynn.boot.Boot import Boot
from orwynn.util.http.http import TestResponse


def test_std(std_mongo_boot: Boot, std_http: HttpClient):
    r: TestResponse = std_http.get("/user/1", 200)

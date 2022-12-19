from pymongo.errors import DuplicateKeyError
from orwynn.base.test.HttpClient import HttpClient
from orwynn.boot.Boot import Boot
from orwynn.util import validation
from orwynn.util.http.http import TestResponse


def test_same_id_creation(std_mongo_boot: Boot, std_http: HttpClient):
    r: TestResponse = std_http.post(
        "/users",
        200,
        json={
            "name": "Mark Watney"
        }
    )
    validation.expect(
        std_http.post,
        DuplicateKeyError,
        "/users",
        200,
        json={
            "id": r.json()["value"]["id"],
            "name": "Mark Watney"
        }
    )

from pymongo.errors import DuplicateKeyError

from orwynn.base.test.HttpClient import HttpClient
from orwynn.boot.Boot import Boot
from orwynn.base.mapping.CustomUseOfMappingReservedFieldError import \
    CustomUseOfMappingReservedFieldError
from orwynn.mongo.MongoMapping import MongoMapping
from orwynn.util import validation
from orwynn.util.web import Response
from tests.std.user import User


def test_user_create(std_mongo_boot: Boot, std_http: HttpClient):
    r: Response = std_http.post(
        "/users",
        200,
        json={
            "name": "Mark Watney"
        }
    )
    created_user: User = User.recover(r.json())
    User.find_one(id=created_user.id)


def test_reserved_mapping_field(std_mongo_boot, std_http: HttpClient):
    class M(MongoMapping):
        mongo_filter: int

    validation.expect(M, CustomUseOfMappingReservedFieldError, mongo_filter=1)


def test_same_id_creation(std_mongo_boot: Boot, std_http: HttpClient):
    r: Response = std_http.post(
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

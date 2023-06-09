from orwynn.http import TestHttpResponse
from orwynn.mapping.errors import CustomUseOfMappingReservedFieldError
from orwynn.mongo.document import Document
from orwynn.mongo.errors import DuplicateKeyError
from orwynn.proxy.boot import BootProxy
from orwynn.testing.client import Client
from orwynn.utils import validation
from tests.std.user import User


def test_user_create(std_mongo_boot, std_http: Client):
    r: TestHttpResponse = std_http.post(
        "/users",
        200,
        json={
            "name": "Mark Watney"
        }
    )
    created_user: User = User.recover(r.json())
    User.find_one({"id": created_user.id})


def test_reserved_mapping_field(std_mongo_boot, std_http: Client):
    class M(Document):
        mongo_filter: int

    validation.expect(M, CustomUseOfMappingReservedFieldError, mongo_filter=1)


def test_same_id_creation(std_mongo_boot, std_http: Client):
    r: TestHttpResponse = std_http.post(
        "/users",
        200,
        json={
            "name": "Mark Watney"
        }
    )
    r2: TestHttpResponse = std_http.post(
        "/users",
        400,
        json={
            "id": r.json()["value"]["id"],
            "name": "Mark Watney"
        }
    )

    validation.validate(
        BootProxy.ie().api_indication.recover(DuplicateKeyError, r2.json()),
        DuplicateKeyError
    )

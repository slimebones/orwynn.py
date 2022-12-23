from pytest import fixture
from orwynn.base.controller.Controller import Controller
from orwynn.base.controller.endpoint.EndpointSpec import EndpointSpec
from orwynn.base.controller.endpoint.endpoint import endpoint
from orwynn.base.model.Model import Model
from orwynn.base.module.Module import Module
from orwynn.boot.Boot import Boot


@fixture
def run_spec():
    class Item(Model):
        name: str
        priority: int

    class Response400(Model):
        message: str
        power: float

    class C1(Controller):
        ROUTE = "/"
        METHODS = ["get"]

        @endpoint(EndpointSpec(
            ResponseModel=Item, default_status_code=201,
            summary="Returns the best item!",
            tags=["best items"],
            response_description="OK",
            is_deprecated=True,
            responses={
                400: {
                    "model": Response400,
                    "description": "Bad things happened!"
                }
            }
        ))
        def get(self) -> Item:
            return Item(name="hello", priority=1)

    Boot(Module(
        route="/",
        Controllers=[C1]
    ))


def test_tmp():
    class Item(Model):
        name: str
        price: float

    class C1(Controller):
        ROUTE = "/"
        METHODS = ["get"]

        @endpoint(EndpointSpec(
            ResponseModel=Item
        ))
        def get(self):
            return Item(name="donut", price=10.5)


    r = Boot(Module(
        route="/",
        Controllers=[C1]
    )).app.http_client.get("/", 200)

    print(r.json())

    assert False

from pytest import fixture
from orwynn.base.controller.Controller import Controller
from orwynn.base.controller.endpoint import EndpointResponse
from orwynn.base.controller.endpoint.Endpoint import Endpoint
from orwynn.base.model.Model import Model
from orwynn.base.module.Module import Module
from orwynn.boot.Boot import Boot


@fixture
def run_endpoint():
    class Item(Model):
        name: str
        price: int

    class Response400(Model):
        message: str
        power: float

    class C1(Controller):
        ROUTE = "/"
        ENDPOINTS = [
            Endpoint(
                method="get",
                ResponseModel=Item,
                default_status_code=201,
                summary="Best summary",
                tags=["best-item", "buy-now"],
                response_description="Best response description",
                is_deprecated=True,
                responses=[
                    EndpointResponse(
                        status_code=400,
                        Entity=ValueError
                    )
                ]
            )
        ]

        def get(self) -> Item:
            return Item(name="hello", price=1)

    Boot(Module(
        route="/",
        Controllers=[C1]
    ))

from orwynn.boot.Boot import Boot
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HTTPController import HTTPController
from orwynn.error.Error import Error
from orwynn.indication.Indication import Indication
from orwynn.indication.IndicationType import IndicationType
from orwynn.indication.Indicator import Indicator
from orwynn.module.Module import Module


def test_custom_status_code():
    class C1(HTTPController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self):
            raise Error("whoops!", status_code=401)

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1])
    )

    boot.app.client.get("/", 401)


def test_default_indication_type():
    class E(Error):
        pass

    i: Indication = Indication({
        "type": Indicator.TYPE,
        "value": Indicator.VALUE
    })

    assert i.digest(E(message="whatever"))["type"] == "error"


def test_custom_indication_type():
    class E(Error):
        # OK for error doesn't make sense in real application, but if in future
        # there will be more indication type, e.g. separation of errors of
        # business logic and http logic, but now an OK is used just for testing
        # purposes.
        INDICATION_TYPE = IndicationType.OK

    i: Indication = Indication({
        "type": Indicator.TYPE,
        "value": Indicator.VALUE
    })

    assert i.digest(E(message="whatever"))["type"] == "ok"

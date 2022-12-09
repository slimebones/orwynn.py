from orwynn.src.base.singleton.singleton import Singleton


class Controller:
    """Handles incoming requests and returns responses to the client.
    
    Calls service or different services under the hood to prepare a response.

    Controller is not a Provider, and it has lower priority than Service which
    means services can be easily injected into controller to be used.

    Controller should be assigned at according Module.controllers field to be
    initialized and registered.

    Class-attributes:
        ROUTE:
            A subroute of Module's route (where controller attached) which
            controller will answer to. This attribute is required to be
            defined in subclasses explicitly or an error will be raised. 
        MIDDLEWARE:
            List of Middleware classes to be applied to this controller.
    """
    ROUTE: str
    MIDDLEWARE: list

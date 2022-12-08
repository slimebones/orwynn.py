from src.base.singleton.singleton import Singleton


class Controller(Singleton):
    """Handles incoming requests and returns responses to the client.
    
    Calls service or different services under the hood to prepare a response.

    Controller is a Provider, and it has lower priority than Service which
    means services can be easily injected into controller to be used.
    """
    pass

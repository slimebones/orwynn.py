class Service:
    """Manages incoming calls to operate on attached business domain.

    Service is a Provider, so it can be injectable. It has higher priority than
    Controllers, since Service never ever need to call a controller, so it
    doesn't have to know about them.
    """

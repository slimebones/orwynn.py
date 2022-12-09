from orwynn.src.base.model.model import Model


class Config(Model):
    """Object holding configuration which can be injected to any requesting
    entity.

    Config is a Provider and has highest priority to be initialized in DI
    chain, so it makes it a perfect candidate to be requested in other entities
    as a configuration model.
    """
    pass

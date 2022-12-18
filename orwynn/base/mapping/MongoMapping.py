from orwynn.base.mapping.Mapping import Mapping


class MongoMapping(Mapping):
    """Mapping to work with MongoDB.

    This is an abstract class. You should subclass it in your application and
    define MODEL class attribute to choose model to work with in this mapping.
    """

    def __init__(self) -> None:
        super().__init__()

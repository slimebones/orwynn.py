from pymongo.cursor import Cursor

from orwynn.base.mapping.Mapping import Mapping


class MongoMapping(Mapping):
    """Mapping to work with MongoDB.

    You should subclass this class in your application and
    define MODEL class attribute to choose model to work with in this mapping.
    """

    def __init__(self) -> None:
        super().__init__()

    def find_all(self, *args, **kwargs) -> Cursor:
        raise NotImplementedError()

    def find_one(self, *args, **kwargs) -> :
        raise NotImplementedError()

    def create(self, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def update(self, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def remove(self, *args, **kwargs) -> Any:
        raise NotImplementedError()

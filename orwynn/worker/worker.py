from orwynn.singleton.singleton import Singleton


class Worker(Singleton):
    """Does framework-related tasks, such as assembling of all app or DI."""
    def __init__(self) -> None:
        super().__init__()

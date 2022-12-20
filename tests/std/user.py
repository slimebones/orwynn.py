from orwynn.base.controller.Controller import Controller
from orwynn.base.module.Module import Module
from orwynn.base.service.Service import Service
from orwynn.mongo.MongoMapping import MongoMapping


class User(MongoMapping):
    name: str
    post_ids: list[str] = []


class UserService(Service):
    def __init__(self) -> None:
        super().__init__()

    def find(self, id: str) -> User:
        return User.find_one(id=id)

    def create(self, user: User) -> User:
        a = user.create()
        print(a.id)
        return a


class UsersController(Controller):
    ROUTE = "/"
    METHODS = ["post"]

    def __init__(self, sv: UserService) -> None:
        super().__init__()
        self.sv = sv

    def post(self, user: User) -> dict:
        return self.sv.create(user).api


class UsersIdController(Controller):
    ROUTE = "/{id}"
    METHODS = ["get"]

    def __init__(self, sv: UserService) -> None:
        super().__init__()
        self.sv = sv

    def get(self, id: str) -> dict:
        return self.sv.find(id).api


user_module = Module(
    route="/users",
    Providers=[UserService],
    Controllers=[UsersController, UsersIdController]
)

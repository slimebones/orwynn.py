from orwynn.base.controller.Controller import Controller
from orwynn.base.controller.endpoint import Endpoint
from orwynn.base.module.Module import Module
from orwynn.base.service.Service import Service
from orwynn.mongo.Document import Document


class User(Document):
    name: str
    post_ids: list[str] = []


class UserService(Service):
    def __init__(self) -> None:
        super().__init__()

    def find(self, id: str) -> User:
        return User.find_one(id=id)

    def create(self, user: User) -> User:
        return user.create()


class UsersController(Controller):
    ROUTE = "/"
    ENDPOINTS = [Endpoint(method="post")]

    def __init__(self, sv: UserService) -> None:
        super().__init__()
        self.sv = sv

    def post(self, user: User) -> dict:
        return self.sv.create(user).api


class UsersIdController(Controller):
    ROUTE = "/{id}"
    ENDPOINTS = [Endpoint(method="get")]

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

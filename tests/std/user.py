from orwynn import mongo
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HttpController import HttpController
from orwynn.module.Module import Module
from orwynn.mongo.Document import Document
from orwynn.mongo.Mongo import Mongo
from orwynn.service.Service import Service


class User(Document):
    name: str
    post_ids: list[str] = []


class UserService(Service):
    def __init__(self, mongo: Mongo) -> None:
        super().__init__()

    def find(self, id: str) -> User:
        return User.find_one({"id": id})

    def create(self, user: User) -> User:
        return user.create()


class UsersController(HttpController):
    ROUTE = "/"
    ENDPOINTS = [Endpoint(method="post")]

    def __init__(self, sv: UserService) -> None:
        super().__init__()
        self.sv = sv

    def post(self, user: User) -> dict:
        return self.sv.create(user).api


class UsersIdController(HttpController):
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
    Controllers=[UsersController, UsersIdController],
    imports=[mongo.module]
)

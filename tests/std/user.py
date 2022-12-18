from orwynn.base.controller.Controller import Controller
from orwynn.base.model.Model import Model
from orwynn.base.module.Module import Module
from orwynn.base.service.Service import Service
from orwynn.mongo.MongoMapping import MongoMapping


class User(MongoMapping):
    name: str
    post_ids: list[str]


class UserService(Service):
    def __init__(self) -> None:
        super().__init__()

    def find(self, id: str) -> User:
        return User.find_one({"_id": id})


class UserIdController(Controller):
    ROUTE = "/{id}"
    METHODS = ["get"]

    def __init__(self, sv: UserService) -> None:
        super().__init__()
        self.__sv = sv

    def get(self, id: str) -> dict:
        return self.__sv.find(id).api


user_module = Module(
    route="/user",
    Providers=[UserService, UserIdController],
    Controllers=[]
)

from orwynn.base.controller.Controller import Controller
from orwynn.base.mapping.MongoMapping import MongoMapping
from orwynn.base.model.Model import Model
from orwynn.base.module.Module import Module
from orwynn.base.service.Service import Service


class User(Model):
    name: str
    post_ids: list[str]


class UserMapping(MongoMapping):
    MODEL = User


class UserService(Service):
    def __init__(self, mapping: UserMapping) -> None:
        super().__init__()
        self.__mapping = mapping

    def find(self, id: str) -> User:
        return self.__mapping.find_one(id=id)


class UserController(Controller):
    ROUTE = "/{id}"
    METHODS = ["get"]

    def __init__(self, sv: UserService) -> None:
        super().__init__()
        self.__sv = sv

    def get(self, id: str) -> dict:
        return self.__sv.find(id).api


user_module = Module(
    route="/user",
    Providers=[UserService, UserMapping, UserController],
    Controllers=[]
)

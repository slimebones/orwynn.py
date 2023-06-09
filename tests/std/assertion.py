from orwynn import mongo
from orwynn.app import App, AppConfig
from orwynn.base.module import Module
from orwynn.boot import BootConfig
from orwynn.di.acceptor import Acceptor
from orwynn.di.provider import Provider
from orwynn.log import LogConfig
from orwynn.mongo import Mongo, MongoConfig
from tests.std.float import FloatController, FloatService, float_module
from tests.std.number import NumberController, NumberService, number_module
from tests.std.rootmodule import root_module
from tests.std.text import TextConfig, TextController, TextService, text_module
from tests.std.user import UserService, UsersIdController, user_module


class Assertion:
    COLLECTED_MODULES: list[Module] = [
        root_module,
        text_module,
        number_module,
        float_module,
        user_module,
        mongo.module
    ]
    # Order of these providers doesn't matter here since set() should be
    # performed on comparison tests
    COLLECTED_PROVIDERS: list[type[Provider]] = [
        App,
        AppConfig,
        LogConfig,
        Mongo,
        MongoConfig,
        TextService,
        TextConfig,
        NumberService,
        FloatService,
        BootConfig,
        UserService
    ]
    COLLECTED_OTHER_ACCEPTORS: list[type[Acceptor]] = [
        TextController,
        NumberController,
        FloatController,
        UsersIdController
    ]

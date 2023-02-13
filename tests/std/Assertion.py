from orwynn import mongo
from orwynn.app.App import App
from orwynn.boot.BootConfig import BootConfig
from orwynn.di.acceptor import Acceptor
from orwynn.di.Provider import Provider
from orwynn.module.Module import Module
from orwynn.mongo.Mongo import Mongo
from orwynn.mongo.MongoConfig import MongoConfig
from tests.std.float import FloatController, FloatService, float_module
from tests.std.number import NumberController, NumberService, number_module
from tests.std.root_module import root_module
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

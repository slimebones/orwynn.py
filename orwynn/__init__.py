"""Scalable web-framework with out-of-the-box architecture."""
# Only base most required imports should be here to not overflow shortcut
# imports, others can be imported from modules directly.
#
# Also it's OK to include framework modules here to import, such as sql_module
# or log_module.
from orwynn.app.App import App
from orwynn.boot.Boot import Boot
from orwynn.boot.BootMode import BootMode
from orwynn.config.Config import Config
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.endpoint.EndpointResponse import EndpointResponse
from orwynn.controller.http.HttpController import HttpController
from orwynn.controller.websocket.WebsocketController import WebsocketController
from orwynn.error.catching.ErrorHandler import ErrorHandler
from orwynn.error.Error import Error
from orwynn.indication.Indication import Indication
from orwynn.indication.IndicationType import IndicationType
from orwynn.indication.Indicator import Indicator
from orwynn.log.Log import Log
from orwynn.middleware.HttpMiddleware import HttpMiddleware
from orwynn.middleware.HttpNextCallFn import HttpNextCallFn
from orwynn.middleware.WebsocketMiddleware import WebsocketMiddleware
from orwynn.middleware.WebsocketNextCallFn import WebsocketNextCallFn
from orwynn.model.Model import Model
from orwynn.module.Module import Module
from orwynn.mongo import module as mongo_module
from orwynn.mongo.Document import Document
from orwynn.proxy.BootProxy import BootProxy
from orwynn.service.Service import Service
from orwynn.sql import module as sql_module
from orwynn.sql.Sql import Sql
from orwynn.sql.Table import Table
from orwynn.testing.Client import Client
from orwynn.testing.EmbeddedTestClient import EmbeddedTestClient
from orwynn.web.websocket.Websocket import Websocket

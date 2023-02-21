"""
Scalable web-framework with out-of-the-box architecture.

Use only two types of imports:
1. from orwynn import something
2. from orwynn.shared.[somemodule] import something

Other imports such as direct ones are discouraged, since structural changes
there are not marked as breaking.
"""
from orwynn import shared

# Only base classes listed here, others go in shared module.
from orwynn.app.App import App
from orwynn.boot.api_version.ApiVersion import ApiVersion
from orwynn.boot.Boot import Boot
from orwynn.boot.BootMode import BootMode
from orwynn.config.Config import Config
from orwynn.error.Error import Error
from orwynn.error.ExceptionHandler import ExceptionHandler
from orwynn.log.Log import Log
from orwynn.model.Model import Model
from orwynn.module.Module import Module
from orwynn.service.Service import Service

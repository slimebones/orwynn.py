from enum import Enum
from src.base.config.config import Config
from src.base.controller.controller import Controller
from src.base.service.service import Service


class ProviderPriorityEnum(Enum):
    """Enumerates Providers and their numeric priorities.

    Higher number - lower priority.
    """
    Config = 1
    Service = 2
    # Controller are lower by priority that service, since a service shouldn't
    # call a controller in any case
    Controller = 3
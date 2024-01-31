from typing import TypeVar

from pydantic import BaseModel


class Cfg(BaseModel):
    """
    Configurational object used to pass initial arguments to the systems.
    """

TCfg = TypeVar("TCfg", bound=Cfg)
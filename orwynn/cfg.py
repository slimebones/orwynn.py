from typing import TypeVar
from pydantic import BaseModel

class Cfg(BaseModel):
    """
    Configurational object used to pass initial arguments to the systems.
    """
    pass

TCfg = TypeVar("TCfg", bound=Cfg)

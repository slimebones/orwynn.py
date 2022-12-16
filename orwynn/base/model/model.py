from pydantic import BaseModel

from orwynn.boot.BootDataProxy import BootDataProxy


class Model(BaseModel):
    """Basic way to represent a data in the app."""
    @property
    def api(self) -> dict:
        """Generates API-complying object using project's defined API
        indication.
        """
        return BootDataProxy.ie().api_indication.digest_model(self)

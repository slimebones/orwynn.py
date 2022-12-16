from pydantic import BaseModel


class Model(BaseModel):
    """Basic way to represent a data in the app."""
    @property
    def api(self) -> dict:
        """Generates API-complying object using project's defined schema."""
        return {
            "type": self.__class__.__name__,
            "value": self.dict
        }

from pydantic import BaseModel


class Flag(BaseModel):
    val: bool

    @staticmethod
    def code():
        return "orwynn__flag"


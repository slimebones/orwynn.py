from pykit.err import ValueErr
from pykit.query import Query
from pykit.res import Res
from result import Err, Ok


class CreateQuery(Query):
    def check(self) -> Res[None]:
        for k in self.keys():
            if k.startswith("$"):
                return Err(ValueErr(f"cannot have operators, got {k}"))
        return Ok(None)

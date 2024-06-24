from typing import Any, Mapping, Sequence, Tuple, Union
from pydantic import BaseModel
from orwynn.mongo import MongoCursor

_SortComplex = Union[
    Sequence[
        Union[str, Tuple[str, Union[int, str, Mapping[str, Any]]]]
    ],
    Mapping[str, Any]
]
_Sort = Union[str, _SortComplex]

class Aggregation(BaseModel):
    sort: _Sort | None = None
    limit: int | None = None

    def apply_to_cursor(self, cursor: MongoCursor) -> MongoCursor:
        if self.sort is not None:
            cursor = cursor.sort(self.sort)
        if self.limit is not None:
            cursor = cursor.limit(self.limit)
        return cursor

"""
Manages data processing.
"""

from typing import Any, Generic, Iterator, Protocol, Self, TypeVar

from ryz.log import log
from ryz.res import Err, Ok, Res

T_contra = TypeVar("T_contra", contravariant=True)

class Pipe(Protocol, Generic[T_contra]):
    def __call__(self, inp: T_contra) -> Res[Any]: ...
class AsyncPipe(Protocol, Generic[T_contra]):
    async def __call__(self, inp: T_contra) -> Res[Any]: ...
TPipe = TypeVar("TPipe", bound=Pipe)

class Pipeline(Generic[T_contra]):
    def __init__(self, *pipes: Pipe[T_contra]) -> None:
        self._line: list[Pipe[T_contra]] = list(pipes)

    def __call__(self, init_val: T_contra) -> Res[T_contra]:
        """
        Calls the pipeline with the initial value, executing all pipes in the
        line, and returning the final result.

        All errors will be wrapped to ``ryz::res::Res``.
        """
        if self.len() == 0:
            return Ok(init_val)

        val = init_val
        last_pipe = self._line[0]
        try:
            for pipe in self._line:
                last_pipe = pipe
                val = pipe(val)
                if isinstance(val, Err):
                    return val
                val = val.okval
        except Exception as err:
            errmsg = f"during executing of pipe {last_pipe}," \
                     f" for value {val} an err {err} occured"
            log.track(err, errmsg)
            return Err(err)

        return Ok(val)

    def __iter__(self) -> Iterator[Pipe[T_contra]]:
        return self._line.__iter__()

    def __len__(self) -> int:
        return self.len()

    def copy(self) -> Self:
        return self.__class__(*self._line)

    def append(self, pipe: Pipe[T_contra]) -> Self:
        self._line.append(pipe)
        return self

    def prepend(self, pipe: Pipe[T_contra]) -> Self:
        self._line.insert(0, pipe)
        return self

    def pop(self) -> Self:
        self._line.pop()
        return self

    def len(self) -> int:
        return len(self._line)

    def merge_right(self, pipeline: Self) -> Self:
        self._line = [*self._line, *pipeline]
        return self

    def merge_left(self, pipeline: Self) -> Self:
        self._line = [*pipeline, *self._line]
        return self

    def is_empty(self) -> bool:
        return self.len == 0

class AsyncPipeline(Generic[T_contra]):
    def __init__(self, *pipes: AsyncPipe[T_contra]) -> None:
        self._line: list[AsyncPipe[T_contra]] = list(pipes)

    async def __call__(self, init_val: T_contra) -> Res[T_contra]:
        """
        Calls the pipeline with the initial value, executing all pipes in the
        line, and returning the final result.

        All errors will be wrapped to ``ryz::res::Res``.
        """
        if self.len() == 0:
            return Ok(init_val)

        val = init_val
        last_pipe = self._line[0]
        try:
            for pipe in self._line:
                last_pipe = pipe
                val = await pipe(val)
                if isinstance(val, Err):
                    return val
                print(pipe)
                val = val.okval
        except Exception as err:
            errmsg = f"during executing of pipe {last_pipe}," \
                     f" for value {val} an err {err} occured"
            log.track(err, errmsg)
            return Err(err)

        return Ok(val)

    def __iter__(self) -> Iterator[AsyncPipe[T_contra]]:
        return self._line.__iter__()

    def __len__(self) -> int:
        return self.len()

    def append(self, pipe: AsyncPipe[T_contra]) -> Self:
        self._line.append(pipe)
        return self

    def copy(self) -> Self:
        return self.__class__(*self._line)

    def prepend(self, pipe: AsyncPipe[T_contra]) -> Self:
        self._line.insert(0, pipe)
        return self

    def pop(self) -> Self:
        self._line.pop()
        return self

    def len(self) -> int:
        return len(self._line)

    def merge_right(self, pipeline: Self) -> Self:
        self._line = [*self._line, *pipeline]
        return self

    def merge_left(self, pipeline: Self) -> Self:
        self._line = [*pipeline, *self._line]
        return self

    def is_empty(self) -> bool:
        return self.len == 0

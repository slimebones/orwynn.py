"""
Transport layer of yon protocol.

Communication is typically managed externally, yon only accept incoming
conections.

For a server general guideline would be to setup external conection manager,
and pass new established conections to ServerBus.con method, where
conection processing further relies on ServerBus.
"""
from asyncio import Queue, Task
from typing import Generic, Protocol, Self, TypeVar, runtime_checkable

from pydantic import BaseModel
from ryz.core import Err, Ok, Res
from ryz.uuid import uuid4

TConCore = TypeVar("TConCore")

# we pass consid to OnSend and OnRecv functions instead of Con to
# not allow these methods to operate on conection, but instead request
# required information about it via the bus
@runtime_checkable
class OnSendFn(Protocol):
    async def __call__(self, consid: str, rbmsg: dict): ...

# generic Protocol[TConMsg] is not used due to variance issues
@runtime_checkable
class OnRecvFn(Protocol):
    async def __call__(self, consid: str, rbmsg: dict): ...

class ConArgs(BaseModel, Generic[TConCore]):
    core: TConCore

    class Config:
        arbitrary_types_allowed = True

class Con(Generic[TConCore]):
    """
    Conection abstract class.

    Methods "recv" and "send" always work with dicts, so implementations
    must perform necessary operations to convert incoming data to dict
    and outcoming data to transport layer's default structure (typically
    bytes). This is dictated by the need to product yon.Msg objects, which
    can be conveniently done only through parsed dict object.
    """
    def __init__(self, args: ConArgs[TConCore]) -> None:
        self._sid = uuid4()
        self._core = args.core
        self._is_closed = False
        self._name: str | None = None

        self._tokens: list[str] = []

    def __aiter__(self) -> Self:
        raise NotImplementedError

    async def __anext__(self) -> dict:
        raise NotImplementedError

    def __str__(self) -> str:
        return f"Con {self.get_display()}"

    @property
    def sid(self) -> str:
        return self._sid

    def get_display(self) -> str:
        return self._name or self._sid

    def get_tokens(self) -> list[str]:
        """
        May also return empty tokens. This would mean that the con is not yet
        registered.
        """
        return self._tokens.copy()

    def set_tokens(self, tokens: list[str]):
        self._tokens = tokens.copy()

    def set_name(self, name: str):
        """
        Sets a name of a connection.
        """
        self._name = name

    def get_name(self) -> Res[str]:
        return Ok(self._name) if self._name else Err(f"undefined {self} name")

    def is_closed(self) -> bool:
        return self._is_closed

    async def recv(self) -> dict:
        raise NotImplementedError

    async def send(self, data: dict):
        raise NotImplementedError

    async def close(self):
        raise NotImplementedError

class Transport(BaseModel):
    is_server: bool
    con_type: type[Con]

    protocol: str = ""
    host: str = ""
    port: int = 0
    route: str = ""

    max_inp_queue_size: int = 10000
    """
    If less or equal than zero, no limitation is applied.
    """
    max_out_queue_size: int = 10000
    """
    If less or equal than zero, no limitation is applied.
    """

    # TODO: add "max_msgs_per_minute" to limit conection's activity

    inactivity_timeout: float | None = None
    """
    Default inactivity timeout for a conection.

    If nothing is received on a conection for this amount of time, it
    is disconected.

    None means no timeout applied.
    """
    mtu: int = 1400
    """
    Max size of a packet that can be sent by the transport.

    Note that this is total size including any headers that could be added
    by the transport.
    """

    on_send: OnSendFn | None = None
    on_recv: OnRecvFn | None = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def url(self) -> str:
        return \
            self.protocol \
            + "://" \
            + self.host \
            + ":" \
            + str(self.port) \
            + "/" \
            + self.route

class ActiveTransport(BaseModel):
    transport: Transport
    inp_queue: Queue[tuple[Con, dict]]
    out_queue: Queue[tuple[Con, dict]]
    inp_queue_processor: Task
    out_queue_processor: Task

    class Config:
        arbitrary_types_allowed = True

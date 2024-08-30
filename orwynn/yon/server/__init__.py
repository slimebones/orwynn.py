"""
Yon server implementation for Python.
"""

# DEV TERMINOLOGY:
#   * rbmsg - Raw Bus Message

import asyncio
import contextlib
import functools
import typing
from asyncio import Queue
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from inspect import isclass, signature
from typing import (
    Any,
    ClassVar,
    Generic,
    Iterable,
    Protocol,
    runtime_checkable,
)

from pydantic import BaseModel
from ryz.code import Code, Coded
from ryz.err import AlreadyProcessedErr, ErrDto, NotFoundErr, ValErr
from ryz.err_utils import create_err_dto
from ryz.log import log
from ryz.ptr import Ptr
from ryz.res import Err, Ok, Res, Result, UnwrapErr, aresultify, valerr
from ryz.singleton import Singleton
from ryz.uuid import uuid4
from yon.server._msg import (
    Bmsg,
    Msg,
    TMsg_contra,
    Welcome,
    ok,
)
from yon.server._rpc import EmptyRpcArgs, RpcFn, RpcRecv, RpcSend
from yon.server._transport import (
    ActiveTransport,
    Con,
    ConArgs,
    OnRecvFn,
    OnSendFn,
    Transport,
)
from yon.server._udp import Udp
from yon.server._ws import Ws

__all__ = [
    "Bus",
    "SubFn",
    "ok",
    "SubOpts",
    "PubOpts",

    "IncorrectYonApiUsageErr",

    "Msg",

    "RpcFn",
    "rpc",
    "RpcSend",
    "RpcRecv",
    "EmptyRpcArgs",
    "StaticCodeid",

    "Con",
    "ConArgs",
    "Transport",
    "Ws",
    "Udp",
    "OnSendFn",
    "OnRecvFn",

    "PubList",
    "InterruptPipeline",
    "SkipMe",

    "sub"
]

class StaticCodeid:
    """
    Static codeids defined by Yon protocol.
    """
    Welcome = 0
    Ok = 1

SubFnRetval = Msg | Iterable[Msg] | None
@runtime_checkable
class SubFn(Protocol, Generic[TMsg_contra]):
    async def __call__(self, msg: TMsg_contra) -> SubFnRetval: ...

def sub(msgtype: type[TMsg_contra]):
    def wrapper(target: SubFn[TMsg_contra]):
        Bus.subfn_init_queue.add((msgtype, target))
        def inner(*args, **kwargs) -> Any:
            return target(*args, **kwargs)
        return inner
    return wrapper

# placed here and not at _rpc.py to avoid circulars
def rpc(key: str):
    def wrapper(target: RpcFn):
        Bus.reg_rpc(key, target).eject()
        def inner(*args, **kwargs) -> Any:
            return target(*args, **kwargs)
        return inner
    return wrapper

class PubList(list[Msg]):
    """
    List of messages to be published.

    Useful as retval from subfn to signify that this list should be unpacked
    and each item be published.
    """

class SkipMe:
    """
    Used by subscribers to prevent any actions on it's retval, since
    returning None will cause bus to publish Ok(None).
    """

class InterruptPipeline:
    def __init__(self, body: Msg) -> None:
        self.body = body

class IncorrectYonApiUsageErr(Exception):
    """
    An error occured at attached resource server, which worked with
    yon api incorrectly.
    """
    @staticmethod
    def code() -> str:
        return "yon::incorrect_yon_api_usage_err"

class InternalInvokedActionUnhandledErr(Exception):
    def __init__(self, action: Callable, err: Exception):
        super().__init__(
            f"invoked {action} unhandled err: {err!r}"
        )

class InternalBusUnhandledErr(Exception):
    def __init__(self, err: Exception):
        super().__init__(
            f"bus unhandled err: {err}"
        )

class PubOpts(BaseModel):
    subfn: SubFn | None = None

    target_consids: list[str] | None = None
    """
    Conection sids to publish to.

    Defaults to only ctx consid, if it exists.
    """

    lsid: str | None = None
    """
    Lsid to be used in the msg.

    Available operators:
        - $ctx::msid - use "msid" field of the ctx as lsid
    """

    send_to_inner: bool = True
    """
    Whether to send to inner bus subscribers.
    """

    send_to_net: bool = True
    """
    Will send to net if True and code is defined for the msg passed.
    """

    pubr_timeout: float | None = None
    """
    Timeout of awaiting for published message response arrival. Defaults to
    None, which means no timeout is set.
    """

    class Config:
        arbitrary_types_allowed = True

MsgCondition = Callable[[Msg], Awaitable[bool]]
MsgFilter = Callable[[Msg], Awaitable[Msg]]
SubFnRetvalFilter = Callable[[SubFnRetval], Awaitable[SubFnRetval]]

class SubOpts(BaseModel):
    recv_last_msg: bool = True
    """
    Whether to receive last stored msg with the same body code.
    """
    conditions: Iterable[MsgCondition] | None = None
    """
    Conditions that must be true in order for the subscriber to be called.

    Are applied to the body only after passing it through ``in_filters``.

    If all conditions fail for a subscriber, it is skipped completely
    (returns RetState.SkipMe).
    """
    inp_filters: Iterable[MsgFilter] | None = None
    out_filters: Iterable[SubFnRetvalFilter] | None = None

_yon_ctx = ContextVar("yon", default={})

@runtime_checkable
class CtxManager(Protocol):
    async def __aenter__(self): ...
    async def __aexit__(self, *args): ...

class BusCfg(BaseModel):
    """
    Global subfn functions are applied **before** local ones passed to SubOpts.
    """

    transports: list[Transport] | None = None
    """
    List of available transport mechanisms.

    For each transport the server bus will be able to accept incoming
    conections and treat them the same.

    "None" enables only default Websocket transport.

    The transports should be managed externally, and established conections
    are passed to ServerBus.con, with ownership transfer.

    If ServerBus.con receive conection not listed in this list, an error
    will be returned.
    """

    reg_types: Iterable[type] | None = None
    """
    Types to register on bus initialization.
    """

    sub_ctxfn: Callable[[Bmsg], Awaitable[Res[CtxManager]]] | None = None
    rpc_ctxfn: Callable[[RpcSend], Awaitable[Res[CtxManager]]] | None = None

    trace_errs_on_pub: bool = True
    log_net_send: bool = True
    log_net_recv: bool = True

    global_subfn_conditions: Iterable[MsgCondition] | None = None
    global_subfn_inp_filters: Iterable[MsgFilter] | None = None
    global_subfn_out_filters: Iterable[SubFnRetvalFilter] | None = None

    consider_sub_decorators: bool = True

    class Config:
        arbitrary_types_allowed = True

class Bus(Singleton):
    """
    Yon server bus implementation.
    """
    subfn_init_queue: ClassVar[set[tuple[type[Msg], SubFn]]] = set()
    """
    Queue of subscription functions to be subscribed on bus's initialization.

    Is not cleared, so after bus recreation, it's no need to reimport all subs.

    Using this queue can be disabled by cfg.consider_sub_decorators.
    """
    _rpckey_to_fn: ClassVar[dict[str, tuple[RpcFn, type[BaseModel]]]] = {}
    DEFAULT_TRANSPORT: ClassVar[Transport] = Transport(
        is_server=True,
        con_type=Ws,
        max_inp_queue_size=10000,
        max_out_queue_size=10000,
        protocol="ws",
        host="localhost",
        port=3000,
        route="rx"
    )
    DEFAULT_CODE_ORDER: ClassVar[list[str]] = [
        "yon::server::welcome",
        "yon::ok"
    ]

    def __init__(self):
        self._is_initd = False

    def get_con_tokens(
            self, consid: str) -> Res[list[str]]:
        con = self._sid_to_con.get(consid, None)
        if con is None:
            return valerr(f"no con with sid {consid}")
        return Ok(con.get_tokens())

    def set_con_tokens(
            self, consid: str, tokens: list[str]) -> Res[None]:
        con = self._sid_to_con.get(consid, None)
        if con is None:
            return valerr(f"no con with sid {consid}")
        con.set_tokens(tokens)
        return Ok(None)

    def get_ctx_con_tokens(self) -> Res[list[str]]:
        consid_res = self.get_ctx_consid()
        if isinstance(consid_res, Err):
            return consid_res
        return self.get_con_tokens(consid_res.okval)

    def set_ctx_con_tokens(
            self, tokens: list[str]) -> Res[None]:
        consid_res = self.get_ctx_consid()
        if isinstance(consid_res, Err):
            return consid_res
        return self.set_con_tokens(consid_res.okval, tokens)

    async def close_con(self, consid: str) -> Res[None]:
        con = self._sid_to_con.get(consid, None)
        if con is None:
            return valerr(f"no con with sid {consid}")
        if con.is_closed:
            return valerr("already closed")
        if consid in self._sid_to_con:
            del self._sid_to_con[consid]
        return await aresultify(con.close())

    def get_ctx(self) -> dict:
        return _yon_ctx.get().copy()

    async def init(self, cfg: BusCfg = BusCfg()):
        if self._is_initd:
            return

        self._cfg = cfg

        self._init_transports()

        self._sid_to_con: dict[str, Con] = {}

        self._subsid_to_code: dict[str, str] = {}
        self._subsid_to_subfn: dict[str, SubFn] = {}
        self._code_to_subfns: dict[str, list[SubFn]] = {}
        self._code_to_last_mbody: dict[str, Msg] = {}

        self._preserialized_welcome_msg: dict = {}

        self._lsid_to_subfn: dict[str, SubFn] = {}
        """
        Subscribers awaiting arrival of linked message.
        """
        self._lsids_to_del_on_next_pubfn: set[str] = set()

        self._is_initd = True
        self._is_post_initd = False

        self._rpc_tasks: set[asyncio.Task] = set()

        reg_types = [] if cfg.reg_types is None else cfg.reg_types
        (await self.reg_types([
            # by yon protocol, welcome msg is always the first, to be
            # recognizable without knowing code ids
            Welcome,
            ok,
            RpcSend,
            RpcRecv,
            ValErr,
            NotFoundErr,
            Coded(
                code="exception",
                val=Exception),
            Coded(
                code="value_error",
                val=ValueError),
            Coded(
                code="type_error",
                val=TypeError),
            Coded(
                code="system_error",
                val=SystemError),
            Coded(
                code="key_error",
                val=KeyError),
            Coded(
                code="attribute_error",
                val=AttributeError),
            *reg_types
        ])).eject()

        if self._cfg.consider_sub_decorators:
            for msgtype, subfn in self.subfn_init_queue:
                (await self.sub(msgtype, subfn)).eject()

    @property
    def is_initd(self) -> bool:
        return self._is_initd

    @classmethod
    async def get_regd_type(cls, code: str) -> Res[type]:
        return await Code.get_regd_type_by_code(code)

    async def reg_types(
        self, types: Iterable[type | Coded[type]]
    ) -> Res[None]:
        """
        Reg codes for types.

        No err is raised on existing code redefinition. Err is printed on
        invalid codes.

        Be careful with this method, once called it enables a lock on msg
        serialization and other processes for the time of codes modification.
        Also, after the reging, all the clients gets notified about
        the changed codes with the repeated welcome message.

        So it's better to be called once and at the start of the program.
        """
        if not self._is_initd:
            return valerr("bus should be initialized")
        upd_res = await Code.upd(types, self.DEFAULT_CODE_ORDER)
        if isinstance(upd_res, Err):
            return upd_res
        return await self._set_welcome()

    @classmethod
    def reg_rpc(
        cls,
        key: str,
        fn: RpcFn,
        msgtype: type[BaseModel] | None = None
    ) -> Res[None]:
        """
        Registers rpc functions for a key.

        # Args

        * key - key for a rpc function
        * fn - rpc function
        * msgtype (optional) - msg type the rpc function will accept. Defaults
                               to provided function's signature for `msg`.
        """
        if key in cls._rpckey_to_fn:
            return Err(ValErr(f"rpc key {key} is already regd"))

        if msgtype is None:
            sig = signature(fn)
            msg_param = sig.parameters.get("msg")
            if not msg_param:
                return valerr(
                    f"rpc fn {fn} with key {key} must accept"
                    " \"msg: AnyBaseModel\" as it's sole argument"
                )
            msgtype = msg_param.annotation
        if msgtype is None:
            return valerr("rpc msg type cannot be None")
        if msgtype is BaseModel:
            return valerr(
                f"rpc fn {fn} with key {key} cannot declare BaseModel"
                " as it's direct args type"
            )
        if not issubclass(msgtype, BaseModel):
            return valerr(
                f"rpc fn {fn} with code {key} must accept args in form"
                f" of BaseModel, got {msgtype}"
            )

        cls._rpckey_to_fn[key] = (fn, msgtype)
        return Ok(None)

    async def postinit(self):
        self._is_post_initd = True

    @classmethod
    async def destroy(cls):
        """
        Should be used only on server close or test interchanging.
        """
        bus = Bus.ie()

        if not bus._is_initd: # noqa: SLF001
            return

        for atransport in bus._con_type_to_atransport.values(): # noqa: SLF001
            atransport.inp_queue_processor.cancel()
            atransport.out_queue_processor.cancel()

        cls._rpckey_to_fn.clear()
        Code.destroy()

        Bus.try_discard()

    async def con(self, con: Con):
        if not self._is_post_initd:
            await self.postinit()

        atransport = self._con_type_to_atransport.get(type(con), None)
        if atransport is None:
            log.err(
                f"cannot find regd transport for con {con}"
                " => close con")
            with contextlib.suppress(Exception):
                await con.close()
        atransport = typing.cast(ActiveTransport, atransport)

        if con.sid in self._sid_to_con:
            log.err("con with such sid already active => skip")
            return

        log.info(f"accept new con {con}", 2)
        self._sid_to_con[con.sid] = con

        try:
            await con.send(self._preserialized_welcome_msg)
            await self._read_ws(con, atransport)
        except Exception as err:
            await log.atrack(err, f"during con {con} main loop => close")
        finally:
            if not con.is_closed():
                try:
                    await con.close()
                except Exception as err:
                    await log.atrack(err, f"during con {con} closing")
            if con.sid in self._sid_to_con:
                del self._sid_to_con[con.sid]

    async def sub(
        self,
        msgtype: type[Msg],
        subfn: SubFn[TMsg_contra],
        opts: SubOpts = SubOpts(),
    ) -> Res[Callable[[], Awaitable[Res[None]]]]:
        """
        Subscribes to certain message.

        Once the message is occured within the bus, the provided action is
        called.

        Args:
            subfn:
                Function to fire once the messsage has arrived.
            opts (optional):
                Subscription options.
        Returns:
            Unsubscribe function.
        """
        if not isclass(msgtype):
            return valerr(f"bodytype {msgtype} should be a class")

        r = self._check_norpc_mbody(msgtype, "subscription")
        if isinstance(r, Err):
            return r
        subsid = uuid4()
        subfn = self._apply_opts_to_subfn(subfn, opts)

        code_res = Code.get_from_type(msgtype)
        if isinstance(code_res, Err):
            return code_res
        code = code_res.okval

        if not Code.has_code(code):
            return valerr(f"code \"{code}\" is not regd")

        if code not in self._code_to_subfns:
            self._code_to_subfns[code] = []
        self._code_to_subfns[code].append(subfn)
        self._subsid_to_subfn[subsid] = subfn
        self._subsid_to_code[subsid] = code

        if opts.recv_last_msg and code in self._code_to_last_mbody:
            last_body = self._code_to_last_mbody[code]
            await self._call_subfn(subfn, last_body)

        return Ok(functools.partial(self.unsub, subsid))

    async def unsub(self, subsid: str) -> Res[None]:
        if subsid not in self._subsid_to_code:
            return Err(ValErr(f"sub with id {subsid} not found"))

        assert self._subsid_to_code[subsid] in self._code_to_subfns

        msg_type = self._subsid_to_code[subsid]

        assert subsid in self._subsid_to_code, "all maps must be synced"
        assert subsid in self._subsid_to_subfn, "all maps must be synced"
        del self._subsid_to_code[subsid]
        del self._subsid_to_subfn[subsid]
        del self._code_to_subfns[msg_type]
        return Ok(None)

    async def unsub_many(
        self,
        sids: list[str],
    ) -> None:
        for sid in sids:
            (await self.unsub(sid)).ignore()

    async def pubr(
        self,
        msg: Msg,
        opts: PubOpts = PubOpts()
    ) -> Res[Msg]:
        """
        Publishes a message and awaits for the response.

        If the response is Exception, it is wrapped to res::Err.
        """
        aevt = asyncio.Event()
        ptr: Ptr[Msg] = Ptr(target=None)

        def wrapper(aevt: asyncio.Event, ptr: Ptr[Msg]):
            async def fn(msg: Msg):
                aevt.set()
                ptr.target = msg
            return fn

        if opts.subfn is not None:
            log.warn("don't pass PubOpts.subfn to pubr, it gets overwritten")
        opts.subfn = wrapper(aevt, ptr)
        pub_res = await self.pub(msg, opts)
        if isinstance(pub_res, Err):
            return pub_res
        if opts.pubr_timeout is None:
            await aevt.wait()
        else:
            try:
                await asyncio.wait_for(aevt.wait(), opts.pubr_timeout)
            except asyncio.TimeoutError as err:
                return Err(err)

        if (isinstance(ptr.target, Exception)):
            return Err(ptr.target)

        return Ok(ptr.target)

    def get_ctx_key(self, key: str) -> Res[Any]:
        val = _yon_ctx.get().get(key, None)
        if val:
            return Ok(val)
        return Err(NotFoundErr(f"\"{key}\" entry in yon ctx"))

    def get_ctx_consid(self) -> Res[str]:
        return self.get_ctx_key("consid")

    async def pub(
        self,
        msg: Msg | Result | Bmsg,
        opts: PubOpts = PubOpts()
    ) -> Res[None]:
        """
        Publishes message to the bus.

        For received UnwrapErr, it's res.errval will be used.

        Received Exceptions are additionally logged if
        cfg.trace_errs_on_pub == True.

        Passed Result will be fetched for the value.
        """
        if isinstance(msg, Ok):
            msg = msg.okval
        elif isinstance(msg, Err):
            msg = msg.errval

        if isinstance(msg, Bmsg):
            bmsg = msg
            msg = bmsg.msg
            code = bmsg.skip__code
        else:
            msg_res = self._make_bmsg(msg, opts)
            if isinstance(msg_res, Err):
                return msg_res
            bmsg = msg_res.okval
            code = bmsg.skip__code

        r = self._check_norpc_mbody(bmsg, "publication")
        if isinstance(r, Err):
            return r

        if opts.subfn is not None:
            if bmsg.sid in self._lsid_to_subfn:
                return Err(AlreadyProcessedErr(f"{bmsg} for pubr"))
            self._lsid_to_subfn[bmsg.sid] = opts.subfn

        self._code_to_last_mbody[code] = msg

        await self._exec_pub_send_order(bmsg, opts)
        return Ok(None)

    def _unpack_err(self, body: Exception, track: bool) -> Msg:
        if isinstance(body, Exception):
            if isinstance(body, UnwrapErr):
                res = body.result
                assert isinstance(res, Err)
                if isinstance(res.errval, Exception):
                    body = res.errval
                else:
                    body = IncorrectYonApiUsageErr(
                        f"got res with err value {res.errval},"
                        " which is not an instance of Exception")
            if track:
                log.track(body, "unpack err")
        return body

    def _unpack_lsid(self, lsid: str | None) -> Res[str | None]:
        if lsid == "$ctx::msid":
            # by default we publish as response to current message, so we
            # use the current's message sid as linked sid
            msid_res = self.get_ctx_key("msid")
            if isinstance(msid_res, Err):
                return msid_res
            lsid = msid_res.okval
            assert isinstance(lsid, str)
        elif isinstance(lsid, str) and lsid.startswith("$"):
            return valerr(f"unrecognized PubOpts.lsid operator: {lsid}")
        return Ok(lsid)

    def _make_bmsg(
        self,
        msg: Msg,
        opts: PubOpts = PubOpts()
    ) -> Res[Bmsg]:
        code_res = Code.get_from_type(type(msg))
        if isinstance(code_res, Err):
            return code_res
        code = code_res.okval
        if not Code.has_code(code):
            return valerr(f"code {code} is not registered")

        msg = self._unpack_err(msg, self._cfg.trace_errs_on_pub)

        lsid_res = self._unpack_lsid(opts.lsid)
        if isinstance(lsid_res, Err):
            return lsid_res
        lsid = lsid_res.okval

        target_consids = None
        if opts.target_consids:
            target_consids = opts.target_consids
        else:
            # try to get ctx consid, otherwise left as none
            consid_res = self.get_ctx_key("consid")
            if isinstance(consid_res, Ok):
                assert isinstance(consid_res.okval, str)
                target_consids = [consid_res.okval]

        return Ok(Bmsg(
            lsid=lsid,
            skip__code=code,
            msg=msg,
            skip__target_consids=target_consids))

    async def _exec_pub_send_order(self, bmsg: Bmsg, opts: PubOpts):
        # SEND ORDER
        #
        #   1. Net
        #   2. Inner
        #   3. As a response

        if opts.send_to_net:
            await self._pub_bmsg_to_net(bmsg)
        if opts.send_to_inner and bmsg.skip__code in self._code_to_subfns:
            await self._send_to_inner_bus(bmsg)
        if bmsg.lsid:
            await self._send_as_linked(bmsg)

    async def _send_to_inner_bus(self, msg: Bmsg):
        subfns = self._code_to_subfns[msg.skip__code]
        if not subfns:
            return
        for subfn in subfns:
            await self._call_subfn(subfn, msg)

    async def _pub_bmsg_to_net(self, bmsg: Bmsg):
        if bmsg.skip__target_consids:
            rbmsg = (await bmsg.serialize_to_net()).unwrap_or(None)
            if rbmsg is None:
                return
            await self._pub_rbmsg_to_net(rbmsg, bmsg.skip__target_consids)

    async def _pub_rbmsg_to_net(self, rbmsg: dict, consids: Iterable[str]):
        for consid in consids:
            if consid not in self._sid_to_con:
                log.err(
                    f"no con with id {consid} for rbmsg {rbmsg}"
                    " => skip")
                continue
            con = self._sid_to_con[consid]
            con_type = type(con)
            # if we have con in self._sid_to_con, we must have transport
            if con_type not in self._con_type_to_atransport:
                log.err("broken state of con_type_to_atransport => skip")
                continue
            atransport = self._con_type_to_atransport[con_type]
            await atransport.out_queue.put((con, rbmsg))

    async def _send_as_linked(self, msg: Bmsg):
        if not msg.lsid:
            return
        subfn = self._lsid_to_subfn.get(msg.lsid, None)
        if subfn is not None:
            await self._call_subfn(subfn, msg)

    def _try_del_subfn(self, lsid: str) -> bool:
        if lsid not in self._lsid_to_subfn:
            return False
        del self._lsid_to_subfn[lsid]
        return True

    def _gen_ctx_dict_for_msg(self, bmsg: Bmsg) -> dict:
        ctx_dict = _yon_ctx.get().copy()

        ctx_dict["msid"] = bmsg.sid
        if bmsg.skip__consid:
            ctx_dict["consid"] = bmsg.skip__consid

        return ctx_dict

    async def _call_subfn(self, subfn: SubFn, bmsg: Bmsg):
        """
        Calls subfn and pubs any response captured (including errors).

        Note that even None response is published as ok(None).
        """
        _yon_ctx.set(self._gen_ctx_dict_for_msg(bmsg))

        if self._cfg.sub_ctxfn is not None:
            try:
                ctx_manager = (await self._cfg.sub_ctxfn(bmsg)).eject()
            except Exception as err:
                await log.atrack(
                    err, f"rpx ctx manager retrieval for body {bmsg.msg}")
                return
            async with ctx_manager:
                retval = await subfn(bmsg.msg)
        else:
            retval = await subfn(bmsg.msg)

        vals = self._parse_subfn_retval(subfn, retval)
        if not vals:
            return

        # by default all subsriber's body are intended to be linked to
        # initial message, so we attach this message ctx msid
        lsid = _yon_ctx.get().get("subfn_lsid", "$ctx::msid")
        pub_opts = PubOpts(lsid=lsid)
        for val in vals:
            val_ = val
            if val_ is None:
                val_ = ok()
            await (await self.pub(val_, pub_opts)).atrack(
                f"during subfn {subfn} retval publication")

    def _parse_subfn_retval(
            self,
            subfn: SubFn,
            retval: SubFnRetval) -> Iterable[Msg]:
        # unpack here, though it can be done inside pub(), but we want to
        # process iterables here
        if isinstance(retval, Ok):
            retval = retval.okval
        if isinstance(retval, Err):
            retval = retval.errval

        if isinstance(retval, SkipMe):
            return []
        if isinstance(retval, InterruptPipeline):
            log.err(
                f"retval {retval} cannot be returned from subfn {subfn}")
            return []
        if isclass(retval):
            log.err(f"subfn {subfn} shouldn't return class {retval}")
            return []

        vals = []
        if isinstance(retval, PubList):
            vals = retval
        else:
            vals = [retval]

        return vals

    def set_ctx_subfn_lsid(self, lsid: str | None):
        """
        Can be used to change subfn lsid behaviour.

        Useful at ``SubOpts.out_filters``, see ``disable_subfn_lsid``.
        """
        ctx_dict = _yon_ctx.get().copy()
        ctx_dict["subfn__lsid"] = lsid

    def _check_norpc_mbody(
            self, body: Msg | type[Msg], disp_ctx: str) -> Res[None]:
        """
        Since rpc msgs cannot participate in actions like "sub" and "pub",
        we have a separate fn to check this.
        """
        iscls = isclass(body)
        if (
            (
                iscls
                and (issubclass(body, RpcSend) or issubclass(body, RpcRecv)))
            or (
                not iscls
                and (isinstance(body, (RpcSend, RpcRecv))))):
            return Err(ValErr(
                f"mbody {body} in context of \"{disp_ctx}\" cannot be"
                " associated with rpc"))
        return Ok(None)

    def _apply_opts_to_subfn(
            self, subfn: SubFn, opts: SubOpts) -> SubFn:
        async def wrapper(msg: Msg) -> Any:
            # globals are applied before locals
            inp_filters = [
                *(self._cfg.global_subfn_inp_filters or []),
                *(opts.inp_filters or [])
            ]
            conditions = [
                *(self._cfg.global_subfn_conditions or []),
                *(opts.conditions or [])
            ]
            out_filters = [
                *(self._cfg.global_subfn_out_filters or []),
                *(opts.out_filters or [])
            ]

            for f in inp_filters:
                msg = await f(msg)
                if isinstance(msg, InterruptPipeline):
                    return msg.body

            for f in conditions:
                flag = await f(msg)
                # if any condition fails, skip the subfn
                if not flag:
                    return SkipMe()

            retbody = await subfn(msg)

            for f in out_filters:
                retbody = await f(retbody)
                if isinstance(retbody, InterruptPipeline):
                    return retbody.body

            return retbody
        return wrapper

    async def _receive_from_con(
            self,
            con: Con,
            atransport: ActiveTransport) -> dict:
        try:
            return await asyncio.wait_for(
                con.recv(),
                atransport.transport.inactivity_timeout)
        except TimeoutError as err:
            raise TimeoutError(
                f"inactivity of con {con} for transport {atransport}"
            ) from err

    async def _read_ws(self, con: Con, atransport: ActiveTransport):
        async for rbmsg in con:
            log.info(f"receive: {rbmsg}", 2)
            atransport.inp_queue.put_nowait((con, rbmsg))

    async def _process_inp_queue(
            self,
            transport: Transport,
            queue: Queue[tuple[Con, dict]]):
        while True:
            con, rbmsg = await queue.get()
            if self._cfg.log_net_recv:
                log.info(f"NET::RECV | {con.sid} | {rbmsg}")
            if transport.on_recv:
                with contextlib.suppress(Exception):
                    # we don't pass whole con to avoid control leaks
                    await transport.on_recv(con.sid, rbmsg)
            bmsg = await self._parse_rbmsg(rbmsg, con)
            if isinstance(bmsg, Err):
                await bmsg.atrack()
                continue
            await self._accept_net_bmsg(bmsg.okval)

    async def _process_out_queue(
            self,
            transport: Transport,
            queue: Queue[tuple[Con, dict]]):
        while True:
            con, rbmsg = await queue.get()

            if self._cfg.log_net_send:
                log.info(f"NET::SEND | {con.sid} | {rbmsg}")

            if transport.on_send:
                with contextlib.suppress(Exception):
                    await transport.on_send(con.sid, rbmsg)

            log.info(f"send to consid {con.sid}: {rbmsg}", 2)

            await con.send(rbmsg)

    async def _accept_net_bmsg(self, bmsg: Bmsg):
        if isinstance(bmsg.msg, RpcRecv):
            log.err(f"server bus won't accept RpcRecv messages, got {bmsg}")
            return
        elif isinstance(bmsg.msg, RpcSend):
            # process rpc in a separate task to not block inp queue
            # processing
            task = asyncio.create_task(self._call_rpc(bmsg))
            self._rpc_tasks.add(task)
            task.add_done_callback(self._rpc_tasks.discard)
            return
        # publish to inner bus with no duplicate net resending
        pub = await self.pub(bmsg, PubOpts(send_to_net=False))
        if isinstance(pub, Err):
            await (
                await self.pub(
                    pub,
                    PubOpts(lsid=bmsg.lsid)
                )
            ).atrack()

    async def _call_rpc(self, bmsg: Bmsg):
        msg = bmsg.msg
        if msg.key not in self._rpckey_to_fn:
            log.err(f"no such rpc code {msg.key} for req {msg} => skip")
            return
        fn, args_type = self._rpckey_to_fn[msg.key]

        _yon_ctx.set(self._gen_ctx_dict_for_msg(bmsg))

        ctx_manager: CtxManager | None = None
        if self._cfg.rpc_ctxfn is not None:
            try:
                ctx_manager = (await self._cfg.rpc_ctxfn(msg)).eject()
            except Exception as err:
                await log.atrack(
                    err,
                    f"rpx ctx manager retrieval for body {msg} => skip")
                return
        try:
            if ctx_manager:
                async with ctx_manager:
                    res = await fn(args_type.model_validate(msg.data))
            else:
                res = await fn(args_type.model_validate(msg.data))
        except Exception as err:
            await log.atrack(
                err, f"rpcfn on req {msg} => wrap to usual RpcRecv")
            res = Err(err)

        val: Any
        if isinstance(res, Ok):
            val = res.okval
        elif isinstance(res, Err):
            val = (await create_err_dto(res.errval)).eject()
            val = typing.cast(ErrDto, val).model_dump(exclude={"stacktrace"})
        else:
            log.err(
                f"rpcfn on req {msg} returned non-res val {res} => skip")
            return

        # val must be any serializable by pydantic object, so here we pass it
        # directly to Msg, which will do serialization automatically under the
        # hood
        evt = Bmsg(
            lsid=bmsg.sid,
            skip__target_consids=[bmsg.skip__consid],
            skip__code=RpcRecv.code(),
            # pass val directly to optimize
            msg=val
        )
        # we publish directly to the net since inner participants can't
        # subscribe to this
        await self._pub_bmsg_to_net(evt)

    async def _parse_rbmsg(
        self, rbmsg: dict, con: Con
    ) -> Res[Bmsg]:
        msid: str | None = rbmsg.get("sid", None)
        if not msid:
            return valerr("msg without sid")
        # msgs coming from net receive conection sid
        rbmsg["skip__consid"] = con.sid
        bmsg = await Bmsg.deserialize_from_net(rbmsg)
        return bmsg

    def _init_transports(self):
        self._con_type_to_atransport: dict[type[Con], ActiveTransport] = {}
        transports = self._cfg.transports
        if not self._cfg.transports:
            transports = [self.DEFAULT_TRANSPORT]
        for transport in typing.cast(list[Transport], transports):
            if transport.con_type in self._con_type_to_atransport:
                log.err(
                    f"con type {transport.con_type} is already regd"
                    " => skip")
                continue
            if not transport.is_server:
                log.err(
                    f"only server transports are accepted, got {transport}"
                    " => skip")
                continue

            inp_queue = Queue(transport.max_inp_queue_size)
            out_queue = Queue(transport.max_out_queue_size)
            inp_task = asyncio.create_task(self._process_inp_queue(
                transport, inp_queue))
            out_task = asyncio.create_task(self._process_out_queue(
                transport, out_queue))
            atransport = ActiveTransport(
                transport=transport,
                inp_queue=inp_queue,
                out_queue=out_queue,
                inp_queue_processor=inp_task,
                out_queue_processor=out_task)
            self._con_type_to_atransport[transport.con_type] = atransport

    async def _set_welcome(self) -> Res[None]:
        codes_res = await Code.get_regd_codes()
        if isinstance(codes_res, Err):
            return codes_res
        codes = codes_res.okval
        welcome = Welcome(codes=codes)
        self._preserialized_welcome_msg = (await Bmsg(
            skip__code=Welcome.code(),
            msg=welcome
        ).serialize_to_net()).eject()
        rewelcome_res = await self._rewelcome_all_cons()
        if isinstance(rewelcome_res, Err):
            return rewelcome_res
        return Ok(None)

    async def _rewelcome_all_cons(self) -> Res[None]:
        return Ok(await self._pub_rbmsg_to_net(
            self._preserialized_welcome_msg,
            self._sid_to_con.keys()))

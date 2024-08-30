"""
Yon server implementation for Python.
"""

# DEV TERMINOLOGY:
#   * rbmsg - Raw Bus Message

import asyncio
import contextlib
import typing
from asyncio import Queue
from contextvars import ContextVar
from inspect import isclass
from typing import (
    Any,
    ClassVar,
    Coroutine,
    Generic,
    Iterable,
    Protocol,
    runtime_checkable,
)

from pydantic import BaseModel
from ryz import log
from ryz.core import Code, Coded, Err, Ok, Res, aresultify, ecode
from ryz.ptr import ptr
from ryz.singleton import Singleton
from ryz.uuid import uuid4

from orwynn.yon.server.msg import (
    Bmsg,
    Msg,
    TMsg_contra,
    Welcome,
    ok,
)
from orwynn.yon.server.transport import (
    ActiveTransport,
    Con,
    ConArgs,
    OnRecvFn,
    OnSendFn,
    Transport,
)
from orwynn.yon.server.udp import Udp
from orwynn.yon.server.ws import Ws

__all__ = [
    "Bus",
    "SubFn",
    "ok",
    "SubOpts",
    "PubOpts",

    "Msg",

    "StaticCodeid",

    "Con",
    "ConArgs",
    "Transport",
    "Ws",
    "Udp",
    "OnSendFn",
    "OnRecvFn",
]

class StaticCodeid:
    """
    Static codeids defined by Yon protocol.
    """
    Welcome = 0
    Ok = 1

@runtime_checkable
class SubFn(Protocol, Generic[TMsg_contra]):
    async def __call__(self, msg: TMsg_contra) -> Res[Msg]: ...

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

class SubOpts(BaseModel):
    recv_last_msg: bool = True

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
    reg_ecodes: Iterable[str] | None = None

    log_net_send: bool = True
    log_net_recv: bool = True

class Bus(Singleton):
    """
    Yon server bus implementation.
    """
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
            return Err(f"no con with sid {consid}")
        return Ok(con.get_tokens())

    def set_con_tokens(
            self, consid: str, tokens: list[str]) -> Res[None]:
        con = self._sid_to_con.get(consid, None)
        if con is None:
            return Err(f"no con with sid {consid}")
        con.set_tokens(tokens)
        return Ok(None)

    def get_ctx_con_tokens(self) -> Res[list[str]]:
        consid_res = self.get_ctx_consid()
        if isinstance(consid_res, Err):
            return consid_res
        return self.get_con_tokens(consid_res.ok)

    def set_ctx_con_tokens(
            self, tokens: list[str]) -> Res[None]:
        consid_res = self.get_ctx_consid()
        if isinstance(consid_res, Err):
            return consid_res
        return self.set_con_tokens(consid_res.ok, tokens)

    async def close_con(self, consid: str) -> Res[None]:
        con = self._sid_to_con.get(consid, None)
        if con is None:
            return Err(f"no con with sid {consid}")
        if con.is_closed:
            return Err("already closed")
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

        (await self.reg_regular_codes(
            # by yon protocol, welcome msg is always the first, to be
            # recognizable without knowing code ids
            Welcome,
            ok,
            *(cfg.reg_types if cfg.reg_types else [])
        )).unwrap()
        self._ecodes: set[str] = set()
        (await self.reg_ecodes(
            ecode.Err,
            ecode.NotFound,
            ecode.Lock,
            ecode.AlreadyProcessed,
            ecode.Panic,
            ecode.Unsupported,
            ecode.Val,
            *(cfg.reg_ecodes if cfg.reg_ecodes else [])
        )).unwrap()
        """
        We use a separate object for error codes, since all of them point to
        the same type - [`Err`].
        """
        self._cached_codes: list[str] = []
        """
        Since order of codes doesn't change, we can maintain a list of
        codes, and renew it on each [`Bus._set_welcome`] call.
        """

    @property
    def is_initd(self) -> bool:
        return self._is_initd

    @classmethod
    async def get_regd_type(cls, code: str) -> Res[type]:
        return await Code.get_regd_type_by_code(code)

    async def reg_regular_codes(
        self, *types: type | Coded[type]
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
            return Err("bus should be initialized")
        upd_res = await Code.upd(types, self.DEFAULT_CODE_ORDER)
        if isinstance(upd_res, Err):
            return upd_res
        return await self._set_welcome()

    async def reg_ecodes(self, *ecodes: str) -> Res[None]:
        self._ecodes.update(*ecodes)
        return await self._set_welcome()

    def get_ecodes(self) -> set[str]:
        return self._ecodes.copy()

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
        msgtype_or_code: type[Msg] | str,
        subfn: SubFn[Msg],
        opts: SubOpts = SubOpts(),
    ) -> Res[Coroutine[Any, Any, None]]:
        """
        Subscribes to certain message.

        Once the message is occured within the bus, the provided action is
        called.

        # Args

        * `subfn` - Function to fire once the messsage has arrived.
        * `opts` - Subscription options.

        # Returns
            Unsubscribe function.
        """
        if isclass(msgtype_or_code):
            subsid = uuid4()
            r = Code.get_from_type(msgtype_or_code)
            if isinstance(r, Err):
                return r
            code = r.ok
        elif not isinstance(msgtype_or_code, str):
            return Err(f"{msgtype_or_code} must be either a type or code")
        else:
            code = msgtype_or_code

        if code not in self.get_cached_codes():
            return Err(f"code \"{code}\" is not regd")

        if code not in self._code_to_subfns:
            self._code_to_subfns[code] = []
        self._code_to_subfns[code].append(subfn)
        self._subsid_to_subfn[subsid] = subfn
        self._subsid_to_code[subsid] = code

        if opts.recv_last_msg and code in self._code_to_last_mbody:
            last_body = self._code_to_last_mbody[code]
            await self._call_subfn(subfn, last_body)

        return Ok(self._unsub_wrapper(subsid)())

    def _unsub_wrapper(self, subsid: str):
        async def inner():
            await self.unsub(subsid)
        return inner

    async def unsub(self, subsid: str):
        if subsid not in self._subsid_to_code:
            log.err(f"sub with id {subsid} not found")
            return None

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
            await self.unsub(sid)

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
        p: ptr[Msg] = ptr(target=None)

        def wrapper(aevt: asyncio.Event, ptr: ptr[Msg]):
            async def fn(msg: Msg) -> Res[None]:
                aevt.set()
                p.target = msg
                return Ok()
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
                return Err.from_native(err)

        if (isinstance(p.target, Exception)):
            return Err.from_native(p.target)

        return Ok(p.target)

    def get_ctx_key(self, key: str) -> Res[Any]:
        val = _yon_ctx.get().get(key, None)
        if val:
            return Ok(val)
        return Err(f"\"{key}\" entry in yon ctx", ecode.NotFound)

    def get_ctx_consid(self) -> Res[str]:
        return self.get_ctx_key("consid")

    def get_ctx_msid(self) -> Res[str]:
        return self.get_ctx_key("msid")

    def get_cached_codes(self) -> list[str]:
        return self._cached_codes

    def get_cached_code_by_codeid(self, codeid: int) -> Res[str]:
        if len(self._cached_codes) - 1 < codeid:
            return Err(f"no such codeid {codeid}", ecode.NotFound)
        return Ok(self._cached_codes[codeid])

    def get_cached_codeid_by_code(self, code: str) -> Res[int]:
        """
        Get a codeid of a registered code or error code.
        """
        for i, c in enumerate(self._cached_codes):
            if code == c:
                return Ok(i)
        return Err(f"{code} not found", ecode.NotFound)

    async def pub(
        self,
        msg: Msg,
        opts: PubOpts = PubOpts()
    ) -> Res[None]:
        """
        Publishes message to the bus.
        """
        if isinstance(msg, Bmsg):
            bmsg = msg
        else:
            r = self._new_bmsg(msg, opts)
            if isinstance(r, Err):
                return r
            bmsg = r.ok
        return await self._pub_bmsg(bmsg, opts)

    async def _pub_bmsg(
        self,
        bmsg: Bmsg,
        opts: PubOpts = PubOpts()
    ) -> Res[None]:
        code = bmsg.skip__code
        if opts.subfn is not None:
            if bmsg.sid in self._lsid_to_subfn:
                return Err(f"{bmsg} for pubr", ecode.AlreadyProcessed)
            self._lsid_to_subfn[bmsg.sid] = opts.subfn

        self._code_to_last_mbody[code] = bmsg.msg

        await self._exec_pub_send_order(bmsg, opts)
        return Ok()

    def _unpack_lsid(self, lsid: str | None) -> Res[str | None]:
        if lsid == "$ctx::msid":
            # by default we publish as response to current message, so we
            # use the current's message sid as linked sid
            msid_res = self.get_ctx_key("msid")
            if isinstance(msid_res, Err):
                return msid_res
            lsid = msid_res.ok
            assert isinstance(lsid, str)
        elif isinstance(lsid, str) and lsid.startswith("$"):
            return Err(f"unrecognized PubOpts.lsid operator: {lsid}")
        return Ok(lsid)

    def _new_bmsg(
        self,
        msg: Msg,
        opts: PubOpts = PubOpts()
    ) -> Res[Bmsg]:
        if isinstance(msg, Err):
            is_err = True
            code = msg.code
        else:
            is_err = False
            r = Code.get_from_type(type(msg))
            if isinstance(r, Err):
                return r
            code = r.ok

        r = self._unpack_lsid(opts.lsid)
        if isinstance(r, Err):
            return r
        lsid = r.ok

        target_consids = None
        if opts.target_consids:
            target_consids = opts.target_consids
        else:
            # try to get ctx consid, otherwise left as none
            consid_res = self.get_ctx_key("consid")
            if isinstance(consid_res, Ok):
                assert isinstance(consid_res.ok, str)
                target_consids = [consid_res.ok]

        return Ok(Bmsg(
            lsid=lsid,
            skip__code=code,
            is_err=is_err,
            msg=msg,
            skip__target_consids=target_consids
        ))

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
            codeid = self.get_cached_codeid_by_code(bmsg.skip__code)
            if isinstance(codeid, Err):
                await codeid.atrack(f"codeid retrieval for {bmsg}")
                return
            codeid = codeid.ok
            rbmsg = await bmsg.serialize_to_net(codeid)
            if isinstance(rbmsg, Err):
                rbmsg = None
            else:
                rbmsg = rbmsg.ok
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
        ret = await subfn(bmsg.msg)
        msg = self._parse_subfn_ret_to_msg(subfn, ret)
        if msg is None:
            # returned None is always converted to `ok()` to ensure the caller
            # receives the response
            msg = ok()

        # by default all subsriber's body are intended to be linked to
        # initial message, so we attach this message ctx msid
        lsid = _yon_ctx.get().get("subfn_lsid", "$ctx::msid")
        pub_opts = PubOpts(lsid=lsid)
        await (await self.pub(msg, pub_opts)).atrack(
            f"during subfn=<{subfn}> return msg=<{msg}> publication"
        )

    def _parse_subfn_ret_to_msg(
        self,
        subfn: SubFn,
        ret: Res[Msg]
    ) -> Msg | Err:
        # unpack here, though it can be done inside pub(), but we want to
        # process iterables here
        if isinstance(ret, Ok):
            final = ret.ok
        elif isinstance(ret, Err):
            final = ret.err
        else:
            final = Err(f"non-result {subfn} ret {ret}")
        return final

    def set_ctx_subfn_lsid(self, lsid: str | None):
        """
        Can be used to change subfn lsid behaviour.

        Useful at ``SubOpts.out_filters``, see ``disable_subfn_lsid``.
        """
        ctx_dict = _yon_ctx.get().copy()
        ctx_dict["subfn__lsid"] = lsid

    async def _recv_from_con(
        self,
        con: Con,
        atransport: ActiveTransport
    ) -> dict:
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

    async def _proc_inp_queue(
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
            await self._accept_net_bmsg(bmsg.ok)

    async def _proc_out_queue(
        self,
        transport: Transport,
        queue: Queue[tuple[Con, dict]]
    ):
        while True:
            con, rbmsg = await queue.get()
            if self._cfg.log_net_send:
                log.info(f"NET::SEND | {con.sid} | {rbmsg}")
            if transport.on_send:
                with contextlib.suppress(Exception):
                    await transport.on_send(con.sid, rbmsg)
            await con.send(rbmsg)

    async def _accept_net_bmsg(self, bmsg: Bmsg):
        # publish to inner bus with no duplicate net resending
        pub = await self._pub_bmsg(
            bmsg,
            PubOpts(send_to_net=False)
        )
        if isinstance(pub, Err):
            await (
                await self.pub(
                    pub,
                    PubOpts(lsid=bmsg.lsid)
                )
            ).atrack()

    async def _parse_rbmsg(
        self, rbmsg: dict, con: Con
    ) -> Res[Bmsg]:
        msid: str | None = rbmsg.get("sid", None)
        if not msid:
            return Err("msg without sid")
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
            inp_task = asyncio.create_task(self._proc_inp_queue(
                transport, inp_queue))
            out_task = asyncio.create_task(self._proc_out_queue(
                transport, out_queue))
            atransport = ActiveTransport(
                transport=transport,
                inp_queue=inp_queue,
                out_queue=out_queue,
                inp_queue_processor=inp_task,
                out_queue_processor=out_task)
            self._con_type_to_atransport[transport.con_type] = atransport

    async def _set_welcome(self) -> Res[None]:
        r = await Code.get_regd_codes()
        if isinstance(r, Err):
            return r
        codes = r.ok
        # we always put error codes after the regular ones
        codes.extend(self._ecodes)
        self._cached_codes = codes.copy()
        welcome = Welcome(codes=codes)
        self._preserialized_welcome_msg = (await Bmsg(
            skip__code=Welcome.code(),
            msg=welcome
        ).serialize_to_net(StaticCodeid.Welcome)).unwrap()
        rewelcome_res = await self._rewelcome_all_cons()
        if isinstance(rewelcome_res, Err):
            return rewelcome_res
        return Ok(None)

    async def _rewelcome_all_cons(self) -> Res[None]:
        return Ok(await self._pub_rbmsg_to_net(
            self._preserialized_welcome_msg,
            self._sid_to_con.keys()))

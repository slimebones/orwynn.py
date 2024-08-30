from typing import Any, Callable, Self, TypeVar

from pydantic import BaseModel
from ryz.core import Code
from ryz import log
from ryz.core import Err, Ok, Res, resultify
from ryz.uuid import uuid4

Msg = Any
TMsg = TypeVar("TMsg", bound=Msg)
TMsg_contra = TypeVar("TMsg_contra", contravariant=True, bound=Msg)
"""
Any custom body bus user interested in. Must be serializable and implement
`code() -> str` method.
"""

class Bmsg(BaseModel):
    """
    Basic unit flowing in the bus.

    Note that any field set to None won't be serialized.

    Fields prefixed with "skip__" won't pass net serialization process.

    Msgs are internal to yon implementation. The bus user is only interested
    in the actual body he is operating on, and which conections they are
    operating with. And the Msg is just an underlying container for that.
    """
    sid: str = ""
    lsid: str | None = None
    """
    Linked message's sid.

    Used to send this message back to the owner of the message with this lsid.
    """

    skip__consid: str | None = None
    """
    From which con the msg is originated.

    Only actual for the server. If set to None, it means that the msg is inner.
    Otherwise it is always set to consid.
    """

    skip__target_consids: list[str] | None = None
    """
    To which consids the published msg should be addressed.
    """

    # since we won't change body type for an existing message, we keep
    # code with the body. Also it's placed here and not in ``msg`` to not
    # interfere with custom fields, and for easier access
    skip__code: str
    """
    Code of msg's body.
    """
    is_err: bool
    """
    Indicates if contained message is an err.
    """
    msg: Msg

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        if "sid" not in data:
            data["sid"] = uuid4()
        super().__init__(**data)

    def __hash__(self) -> int:
        assert self.sid
        return hash(self.sid)

    # todo: use orwynn indication funcs for serialize/deserialize methods

    async def serialize_to_net(self) -> Res[dict]:
        final = self.model_dump()

        msg = final["msg"]
        # don't include empty collections in serialization
        if getattr(msg, "__len__", None) is not None and len(msg) == 0:
            msg = None

        # serialize exception to errdto
        if isinstance(msg, Exception):
            if not isinstance(msg, Err):
                # traceback won't be a thing here so we ignore how many frames
                # we skip
                msg = Err.from_native(msg)
            msg = {"code": msg.code, "msg": msg.msg}

        codeid_res = await Code.get_regd_codeid(self.skip__code)
        if isinstance(codeid_res, Err):
            return codeid_res
        final["codeid"] = codeid_res.ok

        if "skip__consid" in final and final["skip__consid"] is not None:
            # consids must exist only inside server bus, it's probably an err
            # if a msg is tried to be serialized with consid, but we will
            # throw a warning for now, and ofcourse del the field
            log.warn(
                "consids must exist only inside server bus, but it is tried"
                f" to serialize msg {self} with consid != None => ignore"
            )

        keys_to_del = self._get_keys_to_del_from_serialized(final)

        for k in keys_to_del:
            del final[k]

        final["msg"] = msg
        if msg is None and "msg" in final:
            del final["msg"]
        return Ok(final)

    @classmethod
    async def _parse_rbmsg_code(cls, rbmsg: dict) -> Res[str]:
        if "codeid" not in rbmsg:
            return Err(f"msg {rbmsg} must have \"codeid\" field")
        codeid = rbmsg["codeid"]
        del rbmsg["codeid"]
        if not isinstance(codeid, int):
            return Err(
                f"invalid type of codeid {codeid}, expected int"
            )

        code_res = await Code.get_regd_code_by_id(codeid)
        if isinstance(code_res, Err):
            return code_res
        code = code_res.ok
        if not Code.has_code(code):
            return Err(f"unregd code {code}")

        return Ok(code)

    @classmethod
    def _get_keys_to_del_from_serialized(cls, body: dict) -> list[str]:
        keys_to_del: list[str] = []
        is_msid_found = False
        for k, v in body.items():
            if k == "sid":
                is_msid_found = True
                continue
            # all internal or skipped keys are deleted from the final
            # serialization
            if (
                    v is None
                    or k.startswith(("internal__", "skip__"))):
                keys_to_del.append(k)
        if not is_msid_found:
            raise ValueError(f"no sid field for rbmsg {body}")
        return keys_to_del

    @classmethod
    async def _parse_rbmsg_msg(cls, rbmsg: dict) -> Res[Msg]:
        msg = rbmsg.get("msg", None)

        code_res = await cls._parse_rbmsg_code(rbmsg)
        if isinstance(code_res, Err):
            return code_res
        code = code_res.ok

        rbmsg["skip__code"] = code

        custom_type_res = await Code.get_regd_type_by_code(code)
        if isinstance(custom_type_res, Err):
            return custom_type_res
        custom_type = custom_type_res.ok

        deserialize_custom = getattr(custom_type, "deserialize", None)
        final_deserialize_fn: Callable[[], Any]
        if issubclass(custom_type, BaseModel):
            # for case of rbmsg with empty body field, we'll try to initialize
            # the type without any fields (empty dict)
            if msg is None:
                msg = {}
            elif not isinstance(msg, dict):
                return Err(
                    f"if custom type ({custom_type}) is a BaseModel, body"
                    f" {msg} must be a dict, got type {type(msg)}"
                )
            final_deserialize_fn = lambda: custom_type(**msg)
        elif deserialize_custom is not None:
            final_deserialize_fn = lambda: deserialize_custom(msg)
        else:
            # for arbitrary types: just pass body as init first arg
            final_deserialize_fn = lambda: custom_type(msg)

        return resultify(final_deserialize_fn)

    @classmethod
    async def deserialize_from_net(cls, rbmsg: dict) -> Res[Self]:
        """Recovers model of this class using dictionary."""
        # parse body separately according to it's regd type
        msg = await cls._parse_rbmsg_msg(rbmsg)
        if isinstance(msg, Err):
            return msg
        msg = msg.ok

        if "lsid" not in rbmsg:
            rbmsg["lsid"] = None

        rbmsg = rbmsg.copy()
        # don't do redundant serialization of Any type
        rbmsg["msg"] = None
        bmsg = cls.model_validate(rbmsg.copy())
        bmsg.msg = msg
        return Ok(bmsg)

TBmsg = TypeVar("TBmsg", bound=Bmsg)
# lowercase to not conflict with result.Ok
class ok(BaseModel):
    def __str__(self) -> str:
        return "ok message"

    @staticmethod
    def code() -> str:
        # also usable by clients, so the code is without server module prefix
        return "yon::ok"

class Welcome(BaseModel):
    """
    Welcome evt sent to every conected client.
    """
    codes: list[str]

    @staticmethod
    def code() -> str:
        return "yon::server::welcome"

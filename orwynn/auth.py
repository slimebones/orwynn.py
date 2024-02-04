from typing import Callable

import jwt
from fcode import code
from pykit import check
from pykit.dt import DTUtils
from pykit.log import log
from rxcat import Awaitable, Evt, Req

from orwynn.cfg import Cfg
from orwynn.rbac import PermissionModel
from orwynn.sys import Sys


@code("orwynn.login-req")
class LoginReq(Req):
    username: str
    hpassword: str

@code("orwynn.logout-req")
class LogoutReq(Req):
    authToken: str

@code("orwynn.logged-evt")
class LoggedEvt(Evt):
    permissions: list[PermissionModel]
    """
    List of initial permissions the logged user have.

    Subject of further change by rbac evts.
    """

    userSid: str
    userAuthToken: str
    userAuthTokenExp: float

@code("orwynn.logout-evt")
class LogoutEvt(Evt):
    pass

@code("orwynn.auth-err")
class AuthErr(Exception):
    pass

async def _dummy_check_user(req: LoginReq) -> str | None:
    log.warn(
        f"replace dummy check user, received request {req}"
        " => always respond None"
    )
    return None

async def _dummy_set_user_auth_token0(token: str, exp: float):
    log.warn("replace dummy set user auth token")

class AuthCfg(Cfg):
    check_user_func: Callable[[LoginReq], Awaitable[str | None]] = \
        _dummy_check_user
    set_user_auth_token0_and_exp_func: Callable[
        [str, float],
        Awaitable[None]
    ] = _dummy_set_user_auth_token0

    auth_token0_secret: str
    auth_token0_algo: str = "HS256"
    auth_token0_exp_time: float = 2592000  # 30 days

    class Config:
        arbitrary_types_allowed = True

class AuthSys(Sys[AuthCfg]):
    async def init(self):
        pass

    async def enable(self):
        await self._sub(LoginReq, self._on_login_req)

    async def _on_login_req(self, req: LoginReq):
        user_sid = await self._cfg.check_user_func(req)

        if not user_sid:
            raise AuthErr("wrong user data")

        token, exp = self._encode_jwt(user_sid)
        await self._cfg.set_user_auth_token0_and_exp_func(token, exp)
        permissions = [
            PermissionModel(
                code="orwynn-test.test-permission",
                name="Test permission",
                dscr="I'm just a test, don't hurt me."
            )
        ]
        evt = LoggedEvt(
            rsid=req.msid,
            m_toConnids=[req.m_connid] if req.m_connid else [],
            permissions=permissions,
            userSid=user_sid,
            userAuthToken=token,
            userAuthTokenExp=exp
        )
        await self._pub(evt)

    async def _on_logout_req(self, req: LogoutReq):
        await self._pub(LogoutEvt(rsid=req.msid))

    def _encode_jwt(self, user_sid: str) -> tuple[str, float]:
        exp = DTUtils.get_delta_timestamp(self._cfg.auth_token0_exp_time)
        token: str = jwt.encode(
            {
                "userSid": user_sid,
                "exp": exp
            },
            key=self._cfg.auth_token0_secret,
            algorithm=self._cfg.auth_token0_algo
        )

        return token, exp

    def _decode_jwt(
        self,
        auth_token0: str,
        should_verify_exp: bool = True
    ) -> str:
        try:
            data: dict = jwt.decode(
                auth_token0,
                key=self._cfg.auth_token0_secret,
                algorithms=[self._cfg.auth_token0_algo],
                options={
                    "verify_exp": should_verify_exp,
                }
            )
        except jwt.exceptions.ExpiredSignatureError as err:
            raise AuthErr("expired token") from err

        user_sid = data.get("userSid", None)
        check.instance(user_sid, str)
        return user_sid


from typing import Callable

import jwt
from pykit.check import check
from pykit.dt import DtUtils
from pykit.fcode import code
from pykit.log import log
from rxcat import Awaitable, Evt, Req

from orwynn.cfg import Cfg
from orwynn.rbac import PermissionDto, PermissionModel, RbacUtils
from orwynn.sys import Sys


@code("login-req")
class LoginReq(Req):
    username: str
    password: str

@code("logout-req")
class LogoutReq(Req):
    authToken: str

@code("logged-evt")
class LoggedEvt(Evt):
    permissionDtos: list[PermissionDto]
    """
    List of initial permissions the logged user have.

    Subject of further change by rbac evts.
    """

    userSid: str
    userAuthToken: str
    userAuthTokenExp: float

@code("logout-evt")
class LogoutEvt(Evt):
    userSid: str

@code("auth-err")
class AuthErr(Exception):
    pass

async def _dummy_check_user(req: LoginReq) -> str | None:
    log.warn(
        f"replace dummy check user, received request {req}"
        " => always respond None"
    )
    return None

async def _dummy_try_login_user(
    user_sid: str,
    token: str,
    exp: float
) -> list[str] | None:
    log.warn("replace dummy login user => ret None")
    return None

async def _dummy_try_logout_user(user_sid: str) -> bool:
    log.warn("replace dummy logout user => ret False")
    return False

class AuthCfg(Cfg):
    check_user_func: Callable[[LoginReq], Awaitable[str | None]] = \
        _dummy_check_user
    try_login_user: Callable[
        [str, str, float],
        Awaitable[list[str] | None]
    ] = _dummy_try_login_user
    try_logout_user: Callable[[str], Awaitable[bool]] = _dummy_try_logout_user

    auth_token_secret: str
    auth_token_algo: str = "HS256"
    auth_token_exp_time: float = 2592000  # 30 days

    class Config:
        arbitrary_types_allowed = True

class AuthSys(Sys[AuthCfg]):
    async def init(self):
        pass

    async def enable(self):
        await self._sub(LoginReq, self._on_login_req)
        await self._sub(LogoutReq, self._on_logout_req)

    async def _on_login_req(self, req: LoginReq):
        user_sid = await self._cfg.check_user_func(req)

        if not user_sid:
            raise AuthErr("wrong user data")

        token, exp = self._encode_jwt(user_sid)
        permission_codes = await self._cfg.try_login_user(user_sid, token, exp)
        if permission_codes is None:
            raise AuthErr("failed to login user")

        permission_dtos = PermissionModel.to_dtos(
            RbacUtils.get_permissions_by_codes(permission_codes)
        )

        evt = LoggedEvt(
            rsid=req.msid,
            m_toConnids=req.get_res_connids(),
            permissionDtos=permission_dtos,
            userSid=user_sid,
            userAuthToken=token,
            userAuthTokenExp=exp
        )
        log.info(f"logged user sid {user_sid}", 2)
        await self._pub(evt)

    async def _on_logout_req(self, req: LogoutReq):
        # todo: for now logout can be made even with old token, need to ensure
        #       user has this token

        # if token expired, logout must not be prohibited
        user_sid = self._decode_jwt(req.authToken, should_verify_exp=False)
        logout_ok = await self._cfg.try_logout_user(user_sid)
        if not logout_ok:
            raise AuthErr(f"logout for user sid {user_sid} failed")
        log.info(f"logged out user sid {user_sid}", 2)
        await self._pub(
            LogoutEvt(
                rsid=req.msid,
                m_toConnids=req.get_res_connids(),
                userSid=user_sid
            )
        )

    def _encode_jwt(self, user_sid: str) -> tuple[str, float]:
        exp = DtUtils.get_delta_timestamp(self._cfg.auth_token_exp_time)
        token: str = jwt.encode(
            {
                "userSid": user_sid,
                "exp": exp
            },
            key=self._cfg.auth_token_secret,
            algorithm=self._cfg.auth_token_algo
        )

        return token, exp

    def _decode_jwt(
        self,
        auth_token: str,
        should_verify_exp: bool = True
    ) -> str:
        try:
            data: dict = jwt.decode(
                auth_token,
                key=self._cfg.auth_token_secret,
                algorithms=[self._cfg.auth_token_algo],
                options={
                    "verify_exp": should_verify_exp,
                }
            )
        except jwt.exceptions.ExpiredSignatureError as err:
            raise AuthErr("expired token") from err

        user_sid = data.get("userSid", None)
        check.instance(user_sid, str)
        return user_sid


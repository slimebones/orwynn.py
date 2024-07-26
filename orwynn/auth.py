from typing import Any, Callable

import jwt
from pydantic import BaseModel
from pykit.check import check
from pykit.log import log
from pykit.res import Res
from pykit.res import Ok
from rxcat import Awaitable, sub

from orwynn.cfg import Cfg
from orwynn.rbac import PermissionDto, PermissionModel, RbacUtils
from orwynn.sys import Sys


class Login(BaseModel):
    username: str
    password: str

    @staticmethod
    def code():
        return "login"

class Logout(BaseModel):
    auth_token: str

    @staticmethod
    def code():
        return "logout"

class Logged(BaseModel):
    permissions: list[PermissionDto]
    """
    List of initial permissions the logged user have.

    Subject of further change by rbac evts.
    """

    user_sid: str
    user_auth_token: str
    user_auth_token_exp: float

class LoggedOut(BaseModel):
    user_sid: str

    @staticmethod
    def code():
        return "logged_out"

class AuthErr(Exception):
    @staticmethod
    def code():
        return "auth_err"

async def _mock_check_user(req: Login) -> str | None:
    log.warn(
        f"replace dummy check user, received request {req}"
        " => always respond None"
    )
    return None

async def _mock_try_login_user(
    user_sid: str,
    token: str,
    exp: float
) -> list[str] | None:
    log.warn("replace dummy login user => ret None")
    return None

async def _mock_try_logout_user(user_sid: str) -> bool:
    log.warn("replace dummy logout user => ret False")
    return False

class AuthCfg(Cfg):
    check_user_func: Callable[[Login], Awaitable[str | None]] = \
        _mock_check_user
    try_login_user: Callable[
        [str, str, float],
        Awaitable[list[str] | None]
    ] = _mock_try_login_user
    try_logout_user: Callable[[str], Awaitable[bool]] = _mock_try_logout_user

    auth_token_secret: str
    auth_token_algo: str = "HS256"
    auth_token_exp_time: float = 2592000  # 30 days

    class Config:
        arbitrary_types_allowed = True

@sub
async def _on_login_req(self, req: Login):
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

    evt = Logged(
        rsid=req.msid,
        m_target_connsids=req.get_res_connsids(),
        permissions=permission_dtos,
        user_sid=user_sid,
        user_auth_token=token,
        user_auth_token_exp=exp
    )
    log.info(f"logged user sid {user_sid}", 2)
    await self._pub(evt)

async def _on_logout_req(self, req: Logout):
    # todo: for now logout can be made even with old token, need to ensure
    #       user has this token

    # if token expired, logout must not be prohibited
    user_sid = self._decode_jwt(req.auth_token, should_verify_exp=False)
    logout_ok = await self._cfg.try_logout_user(user_sid)
    if not logout_ok:
        raise AuthErr(f"logout for user sid {user_sid} failed")
    log.info(f"logged out user sid {user_sid}", 2)
    await self._pub(
        LoggedOut(
            rsid=req.msid,
            m_target_connsids=req.get_res_connsids(),
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


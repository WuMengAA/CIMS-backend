"""2FA 登录验证与恢复码端点。"""

import secrets
from fastapi import HTTPException
from sqlalchemy import select

from . import totp_routes as mod
from app.models.user import User
from app.services.crypto.totp import verify_totp
from app.services.crypto.recovery import use_recovery_code
from app.services.crypto.token_factory import create_session_token
from app.core.config import REDIS_DB_AUTH
from app.core.redis.accessor import get_redis
from app.api.schemas.totp import TotpVerifyRequest, TotpRecoverRequest

# 临时令牌前缀
_TEMP_PREFIX = "2fa_pending"


@mod.router.post("/verify")
async def verify_2fa_login(body: TotpVerifyRequest):
    """提交 TOTP 码完成登录。"""
    uid = await _pop_temp_token(body.temp_token)
    from app.models.engine import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.id == uid))).scalar_one()
    if not verify_totp(user.totp_secret, body.code):
        raise HTTPException(401, "TOTP 码无效")
    token = await create_session_token(uid)
    return {"token": token, "user_id": uid}


@mod.router.post("/recover")
async def recover_2fa(body: TotpRecoverRequest):
    """使用恢复码完成登录。"""
    uid = await _pop_temp_token(body.temp_token)
    ok = await use_recovery_code(uid, body.recovery_code)
    if not ok:
        raise HTTPException(401, "恢复码无效或已使用")
    token = await create_session_token(uid)
    return {"token": token, "user_id": uid}


async def create_2fa_temp_token(user_id: str) -> str:
    """创建临时令牌用于 2FA 验证流程。"""
    rd = get_redis(REDIS_DB_AUTH)
    token = secrets.token_urlsafe(32)
    await rd.setex(f"{_TEMP_PREFIX}:{token}", 300, user_id)
    return token


async def _pop_temp_token(token: str) -> str:
    """提取并销毁临时令牌，返回 user_id。"""
    rd = get_redis(REDIS_DB_AUTH)
    key = f"{_TEMP_PREFIX}:{token}"
    uid = await rd.get(key)
    if not uid:
        raise HTTPException(401, "临时令牌无效或已过期")
    await rd.delete(key)
    return uid

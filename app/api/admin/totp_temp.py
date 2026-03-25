"""2FA 临时令牌管理。

创建和提取临时令牌用于 TOTP 二次验证流程。
"""

import secrets

from fastapi import HTTPException

from app.core.config import REDIS_DB_AUTH
from app.core.redis.accessor import get_redis

# 临时令牌前缀
_TEMP_PREFIX = "2fa_pending"


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

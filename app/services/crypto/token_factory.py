"""安全会话令牌工厂。

生成 256-bit 加密安全令牌，
存储到 Redis 时绑定 user_id 实现会话追踪。
"""

import secrets
import logging

from app.core.config import REDIS_DB_AUTH
from app.core.redis.accessor import get_redis

logger = logging.getLogger(__name__)

# 256-bit (32 字节) 会话令牌
_TOKEN_BYTES = 32
_DEFAULT_TTL = 3600


async def create_session_token(user_id: str, *, ttl: int = _DEFAULT_TTL) -> str:
    """创建绑定用户身份的会话令牌。

    Args:
        user_id: 用户 UUID。
        ttl: 令牌有效期（秒），默认 1 小时。

    Returns:
        URL 安全的令牌字符串。
    """
    rd = get_redis(REDIS_DB_AUTH)
    token = secrets.token_urlsafe(_TOKEN_BYTES)
    key = f"session:{token}"
    await rd.hset(key, mapping={"user_id": user_id})
    await rd.expire(key, ttl)
    logger.info("会话令牌已创建: user=%s", user_id)
    return token

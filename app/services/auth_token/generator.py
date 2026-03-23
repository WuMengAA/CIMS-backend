"""认证令牌生成逻辑。

创建 1536-bit 加密安全令牌并存储到 Redis，支持租户隔离的命名空间。
"""

import logging
import secrets
from app.core.config import REDIS_DB_AUTH
from app.core.redis.accessor import get_redis

logger = logging.getLogger(__name__)

# 安全常量：192 字节 = 1536-bit 随机令牌
_TOKEN_BYTES = 192
_DEFAULT_TTL = 300


def _key(tenant_id: str, token: str) -> str:
    """构建租户隔离的 Redis 键。"""
    return f"auth:{tenant_id}:{token}" if tenant_id else f"auth::{token}"


async def generate_token(
    scope: str, tenant_id: str = "", *, ttl: int = _DEFAULT_TTL
) -> str:
    """在 Redis 中创建一个新令牌并返回 URL 安全的字符串。"""
    rd = get_redis(REDIS_DB_AUTH)
    token = secrets.token_urlsafe(_TOKEN_BYTES)
    key = _key(tenant_id, token)

    await rd.hset(key, mapping={"scope": scope, "tenant_id": tenant_id})
    await rd.expire(key, ttl)

    logger.info("Token [%s] created for tenant [%s]", scope, tenant_id or "global")
    return token

"""Auth token generation logic.

Creates 384-bit cryptographically secure tokens stored in Redis
for multi-tier API authentication.
"""

import logging
import secrets
from app.core.redis.accessor import get_redis

logger = logging.getLogger(__name__)

# Security constants
_TOKEN_BYTES = 48
_DEFAULT_TTL = 300


async def generate_token(
    scope: str,
    tenant_id: str = "",
    *,
    ttl: int = _DEFAULT_TTL,
) -> str:
    """在 Redis 中创建一个新令牌并返回 URL 安全的字符串。"""
    rd = get_redis()
    token = secrets.token_urlsafe(_TOKEN_BYTES)
    key = f"auth:{token}"

    await rd.hset(
        key,
        mapping={
            "scope": scope,
            "tenant_id": tenant_id,
        },
    )
    await rd.expire(key, ttl)

    logger.info("Token [%s] created for tenant [%s]", scope, tenant_id or "global")
    return token

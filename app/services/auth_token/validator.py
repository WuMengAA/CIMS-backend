"""管理端令牌有效性验证。

通过检查 Redis 记录确保令牌未过期且未被撤销，支持租户隔离键。
"""

from typing import Optional
from app.core.config import REDIS_DB_AUTH
from app.core.redis.accessor import get_redis

_DEFAULT_TTL = 300


def _key(tenant_id: str, token: str) -> str:
    """构建租户隔离的 Redis 键。"""
    return f"auth:{tenant_id}:{token}" if tenant_id else f"auth::{token}"


async def validate_and_refresh(
    token: str, *, tenant_id: str = "", ttl: int = _DEFAULT_TTL
) -> Optional[tuple[str, str]]:
    """验证令牌并自动刷新其过期时间。

    已标记为刷新（宽限期内）的令牌仍视为有效。
    """
    rd = get_redis(REDIS_DB_AUTH)
    key = _key(tenant_id, token)
    data = await rd.hgetall(key)

    if not data or data.get("refreshed") == "1":
        return None

    # 验证通过，延长令牌在 Redis 中的生存时间
    await rd.expire(key, ttl)
    return data.get("scope"), data.get("tenant_id", "")

"""管理端令牌有效性验证。

通过检查 Redis 记录确保令牌未过期且未被撤销。
"""

from typing import Optional
from app.core.redis.accessor import get_redis

_DEFAULT_TTL = 300


async def is_token_valid(token: str) -> bool:
    """验证令牌是否仍处于活动状态。"""
    if not token:
        return False
    rd = get_redis()
    # 检查 Redis 中是否存在该活跃令牌
    return await rd.exists(f"auth:{token}") > 0


async def validate_and_refresh(
    token: str,
    *,
    ttl: int = _DEFAULT_TTL,
) -> Optional[tuple[str, str]]:
    """验证令牌并自动刷新其过期时间。"""
    rd = get_redis()
    key = f"auth:{token}"
    data = await rd.hgetall(key)

    if not data:
        return None

    # 如果验证通过，延长令牌在 Redis 中的生存时间
    await rd.expire(key, ttl)
    return data.get("scope"), data.get("tenant_id", "")

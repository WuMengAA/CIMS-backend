"""管理端令牌注销与黑名单。

提供显式使活动令牌失效的功能。
"""

from app.core.redis.accessor import get_redis


async def revoke_token(token: str) -> None:
    """将令牌添加至 Redis 黑名单。

    Returns:
        True if the token was found and removed.
    """
    if not token:
        return

    rd = get_redis()
    deleted = await rd.delete(f"auth:{token}")
    return deleted > 0

"""针对账户解析的 Redis 缓存层。

通过在 Redis 中存储轻量级账户对象，显著减轻数据库查询压力。
"""

import json
from typing import Optional, TYPE_CHECKING

from app.core.config import REDIS_DB_CACHE
from app.core.redis.accessor import get_redis

if TYPE_CHECKING:
    from app.models.account import Account

# 缓存过期时间（秒）
ACCOUNT_CACHE_TTL = 600


async def get_cached_account(slug: str) -> Optional["Account"]:
    """从 Redis 获取账户详情并重构为轻量级模型对象。"""
    rd = get_redis(REDIS_DB_CACHE)
    cached = await rd.get(f"account:{slug}")
    if not cached:
        return None
    data = json.loads(cached)
    from app.models.account import Account

    return Account(
        id=data["id"],
        name=data["name"],
        slug=data["slug"],
        api_key=data["api_key"],
        is_active=data["is_active"],
    )


async def set_cached_account(slug: str, account: "Account") -> None:
    """将账户记录以 JSON 格式存储于 Redis。"""
    rd = get_redis(REDIS_DB_CACHE)
    await rd.set(
        f"account:{slug}",
        json.dumps(
            {
                "id": account.id,
                "name": account.name,
                "slug": account.slug,
                "api_key": account.api_key,
                "is_active": account.is_active,
            }
        ),
        ex=ACCOUNT_CACHE_TTL,
    )

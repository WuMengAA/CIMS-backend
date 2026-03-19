"""针对租户解析的 Redis 缓存层。

通过在 Redis 中存储轻量级租户对象，显著减轻数据库查询压力。
"""

import json
from typing import Optional
from app.core.redis.accessor import get_redis
from app.models.database import Tenant

TENANT_CACHE_TTL = 600


async def get_cached_tenant(slug: str) -> Optional[Tenant]:
    """从 Redis 获取租户详情并重构为轻量级模型对象。"""
    rd = get_redis()
    cached = await rd.get(f"tenant:{slug}")
    if not cached:
        return None

    data = json.loads(cached)
    return Tenant(
        id=data["id"],
        name=data["name"],
        slug=data["slug"],
        api_key=data["api_key"],
        is_active=data["is_active"],
    )


async def set_cached_tenant(slug: str, tenant: Tenant) -> None:
    """将租户记录以 JSON 格式存储于 Redis，并设置过期时间。"""
    rd = get_redis()
    await rd.set(
        f"tenant:{slug}",
        json.dumps(
            {
                "id": tenant.id,
                "name": tenant.name,
                "slug": tenant.slug,
                "api_key": tenant.api_key,
                "is_active": tenant.is_active,
            }
        ),
        ex=TENANT_CACHE_TTL,
    )

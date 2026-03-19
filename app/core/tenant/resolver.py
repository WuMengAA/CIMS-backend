"""租户解析逻辑，协调 Redis 缓存与 PostgreSQL。

根据 Slug（二级域名标识）安全查找租户的主要接口。
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .cache import get_cached_tenant, set_cached_tenant
from app.models.database import Tenant


async def resolve_tenant(slug: str, db: AsyncSession) -> Optional[Tenant]:
    """根据 slug 解析租户，优先使用缓存，其次查询数据库。"""
    tenant = await get_cached_tenant(slug)
    if tenant is not None:
        return tenant if tenant.is_active else None

    # 数据库查找
    stmt = select(Tenant).where(Tenant.slug == slug)
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()

    if tenant and tenant.is_active:
        await set_cached_tenant(slug, tenant)
        return tenant
    return None

"""单租户资源管理接口。

负责特定租户下课程计划、时段布局等核心配置的明细查询与更新。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.core.redis.accessor import get_redis
from app.api.schemas.tenant import TenantUpdate, TenantOut
from .helpers import get_tenant_or_404, tenant_to_out

router = APIRouter()


@router.get("/{tenant_id}", response_model=TenantOut)
async def get_tenant(tenant_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch profile for a single tenant."""
    tenant = await get_tenant_or_404(tenant_id, db)
    return tenant_to_out(tenant)


@router.put("/{tenant_id}", response_model=TenantOut)
async def update_tenant(
    tenant_id: str, body: TenantUpdate, db: AsyncSession = Depends(get_db)
):
    """Modify metadata for an existing tenant."""
    tenant = await get_tenant_or_404(tenant_id, db)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(tenant, field, value)

    await db.commit()
    await get_redis().delete(f"tenant:{tenant.slug}")
    return tenant_to_out(tenant)


@router.delete("/{tenant_id}")
async def delete_tenant(tenant_id: str, db: AsyncSession = Depends(get_db)):
    """Permanently remove a tenant record."""
    tenant = await get_tenant_or_404(tenant_id, db)
    await get_redis().delete(f"tenant:{tenant.slug}")
    await db.delete(tenant)
    await db.commit()
    return {"status": "success"}

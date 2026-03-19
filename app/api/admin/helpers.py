"""管理端 API 处理器的共有逻辑。

避免在租户序列化和常用对象查找过程中出现代码重复。
"""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import Tenant
from ..schemas.tenant import TenantOut


async def get_tenant_or_404(tenant_id: str, db: AsyncSession) -> Tenant:
    """根据 ID 查找租户，若不存在则报 404。"""
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


def tenant_to_out(t: Tenant) -> TenantOut:
    """将 Tenant 数据库模型格式化为 TenantOut Pydantic Schema。"""
    return TenantOut(
        id=t.id,
        name=t.name,
        slug=t.slug,
        api_key=t.api_key,
        is_active=t.is_active,
        created_at=(t.created_at.isoformat() + "Z" if t.created_at else ""),
    )

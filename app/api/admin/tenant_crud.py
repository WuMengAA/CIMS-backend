"""租户管理接口。

为 CIMS 系统内的组织单位提供标准的创建与列表查询操作。
"""

import secrets
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Tenant, get_db
from app.api.schemas.tenant import TenantCreate, TenantOut
from .helpers import tenant_to_out

router = APIRouter()


@router.post("/", response_model=TenantOut)
async def create_tenant(body: TenantCreate, db: AsyncSession = Depends(get_db)):
    """注册新的教育机构或学校单位。"""
    existing = await db.execute(select(Tenant).where(Tenant.slug == body.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Slug taken")

    tenant = Tenant(
        id=str(uuid.uuid4()),
        name=body.name,
        slug=body.slug,
        api_key=secrets.token_urlsafe(32),
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db.add(tenant)
    await db.commit()
    return tenant_to_out(tenant)


@router.get("/", response_model=list[TenantOut])
async def list_tenants(db: AsyncSession = Depends(get_db)):
    """获取所有已配置的租户列表。"""
    result = await db.execute(select(Tenant))
    return [tenant_to_out(t) for t in result.scalars().all()]

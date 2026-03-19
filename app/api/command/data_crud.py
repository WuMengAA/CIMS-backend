"""基础数据 CRUD 操作。

处理配置文件的创建、列举和删除逻辑。所有操作均在租户隔离下进行。
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.core.tenant.context import get_tenant_id
from app.api.schemas.base import StatusResponse
from .model_map import MODEL_MAP

router = APIRouter()


@router.get("/{resource_type}/create", response_model=StatusResponse)
async def create_data(
    resource_type: str, name: str, db: AsyncSession = Depends(get_db)
):
    """为当前租户创建一个空的配置文件。"""
    tenant_id = get_tenant_id()
    if resource_type not in MODEL_MAP:
        return StatusResponse(status="error", message="无效资源类型")

    model = MODEL_MAP[resource_type]
    new_record = model(
        tenant_id=tenant_id,
        name=name,
        content="{}",
        version=int(datetime.now().timestamp()),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(new_record)
    await db.commit()
    return StatusResponse(status="success", message=f"已创建 {name}")


@router.get("/{resource_type}/list")
async def list_data(resource_type: str, db: AsyncSession = Depends(get_db)):
    """列出指定资源类型下的所有文件名。"""
    tenant_id = get_tenant_id()
    model = MODEL_MAP.get(resource_type)
    if not model:
        return []
    stmt = select(model.name).where(model.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return result.scalars().all()

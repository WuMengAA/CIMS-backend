"""基础数据 CRUD 操作。

处理配置文件的创建与列举。Schema-per-Tenant 隔离。
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.api.schemas.base import StatusResponse
from .model_map import MODEL_MAP

router = APIRouter()


@router.get("/{resource_type}/create", response_model=StatusResponse)
async def create_data(
    resource_type: str, name: str, db: AsyncSession = Depends(get_db)
):
    """为当前租户创建一个空的配置文件。"""
    model = MODEL_MAP.get(resource_type)
    if not model:
        return StatusResponse(status="error", message="无效资源类型")
    existing = await db.execute(select(model).where(model.name == name))
    if existing.scalar_one_or_none():
        return StatusResponse(status="error", message=f"{name} 已存在")
    db.add(
        model(name=name, content="{}", version=0, updated_at=datetime.now(timezone.utc))
    )
    await db.commit()
    return StatusResponse(status="success", message=f"已创建 {name}")


@router.get("/{resource_type}/list")
async def list_data(resource_type: str, db: AsyncSession = Depends(get_db)):
    """列出指定资源类型下的所有文件名。"""
    model = MODEL_MAP.get(resource_type)
    if not model:
        raise HTTPException(status_code=400, detail="无效资源类型")
    result = await db.execute(select(model.name))
    return result.scalars().all()

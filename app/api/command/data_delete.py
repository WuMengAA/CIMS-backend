"""数据删除操作。

处理配置文件的删除逻辑。Schema-per-Tenant 隔离。
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.api.schemas.base import StatusResponse
from .model_map import MODEL_MAP

router = APIRouter()


@router.get("/{resource_type}/delete", response_model=StatusResponse)
@router.delete("/{resource_type}/delete", response_model=StatusResponse)
async def delete_data(
    resource_type: str, name: str, db: AsyncSession = Depends(get_db)
):
    """删除指定的配置文件。"""
    model = MODEL_MAP.get(resource_type)
    if not model:
        return StatusResponse(status="error", message="无效资源类型")
    existing = await db.execute(select(model).where(model.name == name))
    if not existing.scalar_one_or_none():
        return StatusResponse(status="error", message=f"未找到 {name}")
    await db.execute(sql_delete(model).where(model.name == name))
    await db.commit()
    return StatusResponse(status="success", message=f"已删除 {name}")

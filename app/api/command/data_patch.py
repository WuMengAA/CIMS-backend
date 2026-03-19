"""数据合并与深度更新逻辑。

包含字典深度合并工具函数以及 PATCH 增量更新接口实现。
"""

import json
from datetime import datetime, timezone
from fastapi import APIRouter, Body, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.core.tenant.context import get_tenant_id
from app.api.schemas.base import StatusResponse
from .model_map import MODEL_MAP

router = APIRouter()


def dict_deep_merge(base: dict, merge: dict) -> dict:
    """递归合并两个字典，冲突时以 merge 为准。"""
    for key, value in merge.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = dict_deep_merge(base[key], value)
        else:
            base[key] = value
    return base


@router.patch("/{resource_type}/update", response_model=StatusResponse)
async def patch_data(
    resource_type: str,
    name: str,
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """对现有配置执行增量合并更新。"""
    tenant_id = get_tenant_id()
    model = MODEL_MAP.get(resource_type)
    if not model:
        return StatusResponse(status="error", message="无效模型")

    stmt = select(model).where(model.tenant_id == tenant_id, model.name == name)
    record = (await db.execute(stmt)).scalar_one_or_none()
    if not record:
        return StatusResponse(status="error", message="文件未找到")

    current = json.loads(record.content)
    merged = dict_deep_merge(current, payload)
    record.content = json.dumps(merged)
    record.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return StatusResponse(status="success", message="合并成功")

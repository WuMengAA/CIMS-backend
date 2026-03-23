"""数据合并与深度更新逻辑。

PATCH 增量更新接口，含版本校验和负载校验。
"""

import json
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Body, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.api.schemas.base import StatusResponse
from .model_map import MODEL_MAP
from .payload_validator import validate_payload
from .version_check import check_version

router = APIRouter()


def dict_deep_merge(base: dict, merge: dict) -> dict:
    """递归合并两个字典，冲突时以 merge 为准。"""
    for k, v in merge.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k] = dict_deep_merge(base[k], v)
        else:
            base[k] = v
    return base


@router.patch("/{resource_type}/update", response_model=StatusResponse)
async def patch_data(
    resource_type: str,
    name: str,
    payload: dict = Body(...),
    version: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """对现有配置执行增量合并更新。"""
    validate_payload(payload)
    model = MODEL_MAP.get(resource_type)
    if not model:
        return StatusResponse(status="error", message="无效模型")
    record = (
        await db.execute(select(model).where(model.name == name))
    ).scalar_one_or_none()
    if not record:
        return StatusResponse(status="error", message="文件未找到")
    check_version(record, version)
    try:
        current = json.loads(record.content)
    except (json.JSONDecodeError, TypeError):
        current = {}
    record.content = json.dumps(dict_deep_merge(current, payload))
    record.version = (record.version or 0) + 1
    record.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return StatusResponse(status="success", message="合并成功")

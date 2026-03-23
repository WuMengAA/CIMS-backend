"""覆盖式数据写入。

直接替换现有资源 JSON 内容，写入前执行负载与版本校验。
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


@router.post("/{resource_type}/write", response_model=StatusResponse)
@router.put("/{resource_type}/write", response_model=StatusResponse)
async def write_data_endpoint(
    resource_type: str,
    name: str,
    payload: dict = Body(...),
    version: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """写或覆盖指定资源，写入前校验负载和版本。"""
    validate_payload(payload)
    model = MODEL_MAP.get(resource_type)
    if not model:
        return StatusResponse(status="error", message="无效类型")

    stmt = select(model).where(model.name == name)
    record = (await db.execute(stmt)).scalar_one_or_none()
    if record:
        check_version(record, version)
    else:
        record = model(name=name)
    record.content = json.dumps(payload)
    record.version = (record.version or 0) + 1
    record.updated_at = datetime.now(timezone.utc)
    db.add(record)
    await db.commit()
    return StatusResponse(status="success", message=f"{name} 已写入")

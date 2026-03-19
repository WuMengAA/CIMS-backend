"""覆盖式数据写入。

直接替换现有的资源 JSON 内容，并自动更新版本号。
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


@router.post("/{resource_type}/write", response_model=StatusResponse)
@router.put("/{resource_type}/write", response_model=StatusResponse)
async def write_data_endpoint(
    resource_type: str,
    name: str,
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """写或覆盖租户下的指定资源文件内容。"""
    tenant_id = get_tenant_id()
    model = MODEL_MAP.get(resource_type)
    if not model:
        return StatusResponse(status="error", message="无效类型")

    stmt = select(model).where(model.tenant_id == tenant_id, model.name == name)
    record = (await db.execute(stmt)).scalar_one_or_none() or model(
        tenant_id=tenant_id, name=name
    )

    record.content = json.dumps(payload)
    record.version = int(datetime.now().timestamp())
    record.updated_at = datetime.now(timezone.utc)

    db.add(record)
    await db.commit()
    return StatusResponse(status="success", message=f"{name} 已写入")

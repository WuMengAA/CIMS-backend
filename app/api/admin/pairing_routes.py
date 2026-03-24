"""配对码管理 API 路由。

提供配对码的查询、审批、撤销和功能开关接口。
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.models.database import AsyncSessionLocal, get_db
from app.models.system_config import SystemConfig
from app.core.tenant.context import get_tenant_id, set_search_path
from app.services.pairing_utils import (
    get_pairing_by_code,
    approve_pairing,
    revoke_pairing,
    list_pending,
)
from app.core.auth.rbac import require_permission

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pairing", tags=["Pairing"])

_PAIRING_KEY = "pairing_enabled"


class PairingToggle(BaseModel):
    """配对码功能开关请求。"""

    enabled: bool


class PairingCodeDetail(BaseModel):
    """配对码详情响应。"""

    code: str
    client_uid: str = ""
    client_id: str = ""
    client_mac: str = ""
    client_ip: str = ""
    created_at: str = ""
    approved: bool = False
    used: bool = False


class PairingListResponse(BaseModel):
    """配对码列表响应。"""

    codes: list[PairingCodeDetail] = Field(default_factory=list)


async def _is_pairing_enabled() -> bool:
    """读取 system_config 中的配对码开关。"""
    async with AsyncSessionLocal() as db:
        await set_search_path(db)
        stmt = select(SystemConfig).where(SystemConfig.key == _PAIRING_KEY)
        cfg = (await db.execute(stmt)).scalar_one_or_none()
        return cfg is not None and cfg.value == "true"


@router.get(
    "/codes/{code}",
    response_model=PairingCodeDetail,
    dependencies=[Depends(require_permission("pairing.manage"))],
)
async def query_pairing_code(code: str):
    """根据配对码查询设备详情。"""
    tid = get_tenant_id()
    if not tid:
        raise HTTPException(status_code=400, detail="租户上下文缺失")
    record = await get_pairing_by_code(code, tid)
    if not record:
        raise HTTPException(status_code=404, detail="配对码不存在")
    return PairingCodeDetail(
        code=record.code,
        client_uid=record.client_uid,
        client_id=record.client_id,
        client_mac=record.client_mac,
        client_ip=record.client_ip,
        created_at=record.created_at.isoformat() if record.created_at else "",
        approved=record.approved,
        used=record.used,
    )


@router.post(
    "/approve/{code}",
    dependencies=[Depends(require_permission("pairing.manage"))],
)
async def approve_code(code: str):
    """审批配对码，允许对应设备完成注册。"""
    tid = get_tenant_id()
    if not tid:
        raise HTTPException(status_code=400, detail="租户上下文缺失")
    ok = await approve_pairing(code, tid)
    if not ok:
        raise HTTPException(status_code=404, detail="配对码不存在或已使用")
    return {"status": "success", "message": f"配对码 {code} 已审批"}


@router.delete(
    "/codes/{code}",
    dependencies=[Depends(require_permission("pairing.manage"))],
)
async def delete_code(code: str):
    """撤销/删除配对码。"""
    tid = get_tenant_id()
    if not tid:
        raise HTTPException(status_code=400, detail="租户上下文缺失")
    ok = await revoke_pairing(code, tid)
    if not ok:
        raise HTTPException(status_code=404, detail="配对码不存在")
    return {"status": "success", "message": f"配对码 {code} 已撤销"}


@router.get(
    "/codes",
    response_model=PairingListResponse,
    dependencies=[Depends(require_permission("pairing.manage"))],
)
async def list_codes():
    """列出当前租户所有待处理的配对码。"""
    tid = get_tenant_id()
    if not tid:
        raise HTTPException(status_code=400, detail="租户上下文缺失")
    records = await list_pending(tid)
    codes = [
        PairingCodeDetail(
            code=r.code,
            client_uid=r.client_uid,
            client_id=r.client_id,
            client_mac=r.client_mac,
            client_ip=r.client_ip,
            created_at=r.created_at.isoformat() if r.created_at else "",
            approved=r.approved,
            used=r.used,
        )
        for r in records
    ]
    return PairingListResponse(codes=codes)


@router.put(
    "/toggle",
    dependencies=[Depends(require_permission("pairing.manage"))],
)
async def toggle_pairing(body: PairingToggle):
    """启用或关闭配对码功能。"""
    async with AsyncSessionLocal() as db:
        await set_search_path(db)
        stmt = select(SystemConfig).where(SystemConfig.key == _PAIRING_KEY)
        cfg = (await db.execute(stmt)).scalar_one_or_none()
        if not cfg:
            cfg = SystemConfig(
                key=_PAIRING_KEY,
                value="true" if body.enabled else "false",
                updated_at=datetime.now(timezone.utc),
            )
            db.add(cfg)
        else:
            cfg.value = "true" if body.enabled else "false"
            cfg.updated_at = datetime.now(timezone.utc)
        await db.commit()
    state = "已启用" if body.enabled else "已关闭"
    return {"status": "success", "message": f"配对码功能{state}"}

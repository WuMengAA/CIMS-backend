"""客户端在线状态监控。

提供租户下所有终端的在线/离线状态查询、IP 追踪以及详细记录查看。
"""

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db, ClientRecord
from app.core.tenant.context import get_tenant_id

router = APIRouter()


@router.get("/clients/status")
async def get_all_status(request: Request):
    """获取当前租户下所有在线客户端的精简状态列表。"""
    tenant_id = get_tenant_id()
    sm = getattr(request.app.state, "session_manager", None)
    if not sm:
        return []
    return await sm.get_all_clients_status(tenant_id)


@router.get("/client/{uid}/details")
async def get_client_detail(
    uid: str, request: Request, db: AsyncSession = Depends(get_db)
):
    """查询特定客户端的注册详情及其当前在线状态。"""
    tenant_id = get_tenant_id()
    stmt = select(ClientRecord).where(
        ClientRecord.tenant_id == tenant_id, ClientRecord.uid == uid
    )
    record = (await db.execute(stmt)).scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="未找到设备")

    sm = getattr(request.app.state, "session_manager", None)
    online = await sm.is_client_online(tenant_id, uid) if sm else False

    return {
        "uid": record.uid,
        "name": record.client_id,
        "mac": record.mac,
        "status": "online" if online else "offline",
        "registered_at": (
            record.registered_at.isoformat() if record.registered_at else None
        ),
    }

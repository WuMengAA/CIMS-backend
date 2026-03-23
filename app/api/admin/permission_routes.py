"""权限管理路由。

提供权限定义查询、授予和撤销端点。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import get_db
from app.models.permission_def import PermissionDef
from app.core.auth.dependencies import require_role
from app.api.schemas.permission import (
    PermissionGrantRequest,
    PermissionRevokeRequest,
    PermissionDefOut,
)
from app.services.permission.grants import (
    grant_permission,
    revoke_permission,
)

router = APIRouter()
_admin = require_role(90)


@router.get("/defs", response_model=list[PermissionDefOut])
async def list_permission_defs(
    db: AsyncSession = Depends(get_db),
    _user=Depends(_admin),
):
    """查询所有权限定义（需管理员）。"""
    result = await db.execute(select(PermissionDef))
    return [
        PermissionDefOut(code=p.code, label=p.label, category=p.category)
        for p in result.scalars().all()
    ]


@router.post("/grant")
async def grant(
    body: PermissionGrantRequest,
    db: AsyncSession = Depends(get_db),
    _user=Depends(_admin),
):
    """授予或显式拒绝成员权限（需管理员）。"""
    perm = await grant_permission(
        body.member_id, body.permission_code, db, granted=body.granted
    )
    return {"status": "success", "id": perm.id}


@router.post("/revoke")
async def revoke(
    body: PermissionRevokeRequest,
    db: AsyncSession = Depends(get_db),
    _user=Depends(_admin),
):
    """撤销成员权限覆盖（需管理员）。"""
    ok = await revoke_permission(body.member_id, body.permission_code, db)
    if not ok:
        raise HTTPException(status_code=404, detail="权限记录不存在")
    return {"status": "success"}

"""配对码审批路由。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenant.context import get_tenant_id
from app.models.session import get_db
from app.models.pairing import PairingCode

router = APIRouter()


@router.post("/{pairing_id}/reject")
async def reject_pairing(
    pairing_id: str,
    db: AsyncSession = Depends(get_db),
):
    """拒绝（撤销）配对码。"""
    tid = get_tenant_id()
    row = (
        await db.execute(
            select(PairingCode).where(
                PairingCode.id == pairing_id,
                PairingCode.tenant_id == tid,
            )
        )
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(404, "配对码不存在")
    await db.delete(row)
    await db.commit()
    return {"message": f"配对码 {pairing_id} 已拒绝"}


@router.post("/{pairing_id}/approve")
async def approve_pairing_code(
    pairing_id: str,
    db: AsyncSession = Depends(get_db),
):
    """批准配对码。"""
    tid = get_tenant_id()
    row = (
        await db.execute(
            select(PairingCode).where(
                PairingCode.id == pairing_id,
                PairingCode.tenant_id == tid,
            )
        )
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(404, "配对码不存在")
    row.approved = True
    await db.commit()
    return {"message": f"配对码 {pairing_id} 已批准"}

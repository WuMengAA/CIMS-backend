"""配对码管理路由。

提供配对码的列表和搜索接口。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenant.context import get_tenant_id
from app.models.session import get_db
from app.models.pairing import PairingCode
from app.api.schemas.pairing import PairingCodeOut

router = APIRouter()


@router.post("/list", response_model=list[PairingCodeOut])
async def list_pairing_codes(
    db: AsyncSession = Depends(get_db),
):
    """列出当前账户的配对码。"""
    tid = get_tenant_id()
    if not tid:
        raise HTTPException(400, "租户上下文缺失")
    rows = (
        await db.execute(
            select(PairingCode).where(PairingCode.tenant_id == tid)
        )
    ).scalars().all()
    return [
        PairingCodeOut(
            id=r.id,
            code=r.code,
            client_uid=getattr(r, "client_uid", ""),
            approved=getattr(r, "approved", False),
            used=getattr(r, "used", False),
            created_at=str(getattr(r, "created_at", "")),
        )
        for r in rows
    ]

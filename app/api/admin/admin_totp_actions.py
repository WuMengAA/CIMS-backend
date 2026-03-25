"""超管 2FA 禁用路由。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import require_role
from app.models.session import get_db
from app.models.user import User

router = APIRouter()
_sa = require_role(100)


@router.post("/{user_id}/2fa/disable")
async def admin_disable_2fa(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _user=Depends(_sa),
):
    """禁用指定用户的 TOTP。"""
    user = (
        await db.execute(select(User).where(User.id == user_id))
    ).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "用户不存在")
    user.totp_enabled = False
    user.totp_secret = None
    await db.commit()
    return {"message": "2FA 已禁用"}

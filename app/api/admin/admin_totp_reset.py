"""超管 2FA 重置路由。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import require_role
from app.models.session import get_db
from app.models.user import User
from app.services.crypto.totp import generate_totp_secret

router = APIRouter()
_sa = require_role(100)


@router.post("/{user_id}/2fa/reset")
async def admin_reset_2fa(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _user=Depends(_sa),
):
    """重置指定用户的 TOTP 密钥。"""
    user = (
        await db.execute(select(User).where(User.id == user_id))
    ).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "用户不存在")
    user.totp_secret = generate_totp_secret()
    user.totp_enabled = False
    await db.commit()
    return {"message": "TOTP 已重置"}

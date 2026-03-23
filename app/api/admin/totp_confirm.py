"""2FA 确认绑定与禁用端点。"""

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import totp_routes as mod
from app.models.session import get_db
from app.models.user import User
from app.core.auth.dependencies import get_current_user_id
from app.services.crypto.totp import verify_totp
from app.services.crypto.hasher import verify_password
from app.api.schemas.totp import TotpConfirmRequest, TotpDisableRequest


@mod.router.post("/confirm")
async def confirm_2fa(
    body: TotpConfirmRequest,
    uid: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """提交 TOTP 码确认绑定。"""
    user = (await db.execute(select(User).where(User.id == uid))).scalar_one()
    if not user.totp_secret:
        raise HTTPException(400, "请先调用 /enable")
    if not verify_totp(user.totp_secret, body.code):
        raise HTTPException(400, "TOTP 码无效")
    user.totp_enabled = True
    await db.commit()
    return {"status": "2fa_enabled"}


@mod.router.post("/disable")
async def disable_2fa(
    body: TotpDisableRequest,
    uid: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """禁用 2FA（需验证密码）。"""
    user = (await db.execute(select(User).where(User.id == uid))).scalar_one()
    if not verify_password(body.password, user.hashed_password):
        raise HTTPException(401, "密码错误")
    user.totp_enabled = False
    user.totp_secret = None
    await db.commit()
    return {"status": "2fa_disabled"}

"""2FA 启用与管理端点。

提供启用、确认绑定和禁用 2FA 的接口。
"""

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import totp_routes as mod
from app.models.session import get_db
from app.models.user import User
from app.core.auth.dependencies import get_current_user_id
from app.services.crypto.totp import generate_totp_secret, get_totp_uri
from app.services.crypto.recovery import (
    generate_recovery_codes,
    store_recovery_codes,
)
from app.api.schemas.totp import (
    TotpEnableResponse,
)


@mod.router.post("/enable", response_model=TotpEnableResponse)
async def enable_2fa(
    uid: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """生成 TOTP 密钥并返回 URI 和恢复码。"""
    user = (await db.execute(select(User).where(User.id == uid))).scalar_one()
    if user.totp_enabled:
        raise HTTPException(400, "2FA 已启用")
    secret = generate_totp_secret()
    user.totp_secret = secret
    await db.commit()
    codes = generate_recovery_codes()
    await store_recovery_codes(uid, codes)
    return TotpEnableResponse(
        secret=secret,
        uri=get_totp_uri(secret, user.email),
        recovery_codes=codes,
    )

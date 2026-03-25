"""2FA 恢复码登录端点。"""

from fastapi import HTTPException

from . import totp_routes as mod
from app.services.crypto.recovery import use_recovery_code
from app.services.crypto.token_factory import create_session_token
from app.api.schemas.totp import TotpRecoverRequest
from .totp_temp import _pop_temp_token


@mod.router.post("/recover")
async def recover_2fa(body: TotpRecoverRequest):
    """使用恢复码完成登录。"""
    uid = await _pop_temp_token(body.temp_token)
    ok = await use_recovery_code(uid, body.recovery_code)
    if not ok:
        raise HTTPException(401, "恢复码无效或已使用")
    token = await create_session_token(uid)
    return {"token": token, "user_id": uid}

"""管理端身份认证处理器。

管理使用 ADMIN_SECRET 的登录以及令牌注销逻辑。
"""

from fastapi import APIRouter, Body, HTTPException, Request
from app.core.config import ADMIN_SECRET
from app.api.schemas.auth import TokenResponse, AdminLoginRequest
from app.services import auth_token

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def admin_login(
    payload: AdminLoginRequest = Body(...),
):
    """通过全局管理密钥兑换 Admin Bearer 令牌。"""
    if payload.secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    token = await auth_token.generate_token("admin")
    return TokenResponse(token=token)


@router.post("/logout")
async def admin_logout(request: Request):
    """使当前的 Admin 会话失效并注销。"""
    auth = request.headers.get("authorization", "")
    bearer = auth[7:] if auth.startswith("Bearer ") else ""
    if bearer:
        await auth_token.revoke_token(bearer)
    return {"status": "success", "message": "Logged out"}

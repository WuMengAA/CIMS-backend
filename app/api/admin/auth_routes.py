"""管理端身份认证处理器。

提供用户注册和登录端点，支持 TOTP 2FA 流程。
"""

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import get_db
from app.api.schemas.user import UserRegisterRequest, UserLoginRequest
from app.api.schemas.auth import TokenResponse, MessageResponse
from app.services.user.register import register_user
from app.services.user.login import login_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def user_register(
    payload: UserRegisterRequest = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """注册新用户并自动创建关联账户。"""
    try:
        user = await register_user(
            payload.username,
            payload.email,
            payload.password,
            payload.display_name,
            db,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    from app.services.crypto.token_factory import create_session_token

    token = await create_session_token(user.id)
    return TokenResponse(token=token)


@router.post("/login")
async def user_login(
    payload: UserLoginRequest = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """用户登录，支持 2FA 流程。"""
    try:
        token, user, needs_2fa = await login_user(
            payload.email,
            payload.password,
            db,
        )
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    if needs_2fa:
        from app.api.admin.totp_verify import create_2fa_temp_token

        temp = await create_2fa_temp_token(user.id)
        return {"requires_2fa": True, "temp_token": temp}
    return {"token": token}


@router.post("/logout", response_model=MessageResponse)
async def user_logout(request=None):
    """注销当前用户会话。"""
    if request:
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            from app.core.redis.accessor import get_redis
            from app.core.config import REDIS_DB_AUTH

            rd = get_redis(REDIS_DB_AUTH)
            await rd.delete(f"session:{auth[7:]}")
    return MessageResponse(message="已登出")

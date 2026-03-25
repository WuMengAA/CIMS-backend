"""用户注册申请端点。

新用户提交注册后进入 Pending 状态，需管理员审核。
仅需邮箱和密码，用户名自动随机生成。
"""

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.auth import MessageResponse
from app.api.schemas.user import UserRegisterRequest
from app.models.session import get_db
from app.services.user.register import register_user

router = APIRouter()


@router.post("/apply", response_model=MessageResponse)
async def apply_user(
    payload: UserRegisterRequest = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """申请注册新用户（Pending 状态）。"""
    try:
        await register_user(
            payload.email,
            payload.password,
            payload.display_name,
            db,
            username=payload.username,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return MessageResponse(message="注册成功，等待管理员审核")

"""超管用户创建路由。"""

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.user import UserRegisterRequest
from app.api.schemas.user_out import UserOut
from app.core.auth.dependencies import require_role
from app.models.session import get_db
from app.services.user.register import register_user
from .user_helpers import _to_out

router = APIRouter()
_sa = require_role(100)


@router.post("/create", response_model=UserOut)
async def create_user(
    payload: UserRegisterRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    _user=Depends(_sa),
):
    """创建新用户（超管直接创建，跳过审核）。"""
    try:
        user = await register_user(
            payload.email,
            payload.password,
            payload.display_name,
            db,
            username=payload.username,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _to_out(user)

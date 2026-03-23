"""用户管理路由。

提供用户列表查询、详情查看和资料更新端点，
需要超级管理员权限。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import get_db
from app.core.auth.dependencies import require_role
from app.api.schemas.user import UserOut, UserUpdateRequest
from app.services.user.manager import (
    list_users,
    get_user_by_id,
    update_user,
)

router = APIRouter()

# 需要超级管理员权限（priority>=100）
_superadmin = require_role(100)


@router.get("", response_model=list[UserOut])
async def list_all_users(
    offset: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    _user=Depends(_superadmin),
):
    """分页查询所有用户（需超级管理员）。"""
    users, _ = await list_users(db, offset=offset, limit=limit)
    return [_to_out(u) for u in users]


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _user=Depends(_superadmin),
):
    """查询单个用户详情（需超级管理员）。"""
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return _to_out(user)


@router.patch("/{user_id}", response_model=UserOut)
async def patch_user(
    user_id: str,
    body: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _user=Depends(_superadmin),
):
    """更新用户资料（需超级管理员）。"""
    updated = await update_user(user_id, db, **body.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="用户不存在")
    return _to_out(updated)


def _to_out(user) -> UserOut:
    """将 User 模型转换为响应模型。"""
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        display_name=user.display_name,
        role_code=user.role_code,
        is_active=user.is_active,
        created_at=str(user.created_at),
    )

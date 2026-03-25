"""用户信息查询端点。

返回当前已认证用户的基本资料信息。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.user_out import UserOut
from app.core.auth.dependencies import get_current_user_id
from app.models.session import get_db
from app.models.user import User

router = APIRouter()


@router.get("/info", response_model=UserOut)
async def get_user_info(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """获取当前用户信息。"""
    row = await db.execute(select(User).where(User.id == user_id))
    user = row.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        display_name=user.display_name,
        role_code=user.role_code,
        is_active=user.is_active,
        can_create_account=user.can_create_account,
        created_at=str(user.created_at),
    )

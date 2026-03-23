"""用户 CRUD 管理服务。

提供用户列表查询、单用户查询、资料更新、
封禁/激活等管理操作（需超级管理员权限）。
"""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def list_users(
    db: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 20,
) -> tuple[list[User], int]:
    """分页查询用户列表，返回 (用户列表, 总数)。"""
    total = await db.scalar(select(func.count(User.id)))
    result = await db.execute(select(User).offset(offset).limit(limit))
    return list(result.scalars().all()), total or 0


async def get_user_by_id(user_id: str, db: AsyncSession) -> Optional[User]:
    """通过 ID 查询单个用户。"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def update_user(
    user_id: str,
    db: AsyncSession,
    **fields: str,
) -> Optional[User]:
    """更新用户指定字段。"""
    user = await get_user_by_id(user_id, db)
    if not user:
        return None
    for key, val in fields.items():
        if hasattr(user, key) and val is not None:
            setattr(user, key, val)
    await db.commit()
    return user

"""用户审核服务 — 审核通过。

审核通过时激活用户并创建默认账户。
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from .approval import _get_pending_user
from .approval_account import _create_default_account


async def approve_user(
    user_id: str,
    db: AsyncSession,
    *,
    can_create_account: bool = False,
) -> Optional[User]:
    """审核通过：激活用户 → 创建默认账户 → 绑定 owner。"""
    user = await _get_pending_user(user_id, db)
    if not user:
        return None
    # 激活用户
    user.role_code = "normal"
    user.is_active = True
    user.can_create_account = can_create_account
    # 创建默认账户
    await _create_default_account(user, db)
    await db.commit()
    return user

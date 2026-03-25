"""用户注册服务。

注册流程：校验唯一性 → 哈希密码 → 创建 Pending 用户。
用户名可选，留空时自动随机生成。
"""

import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.crypto.hasher import hash_password


def _random_username() -> str:
    """生成随机用户名（user_ + 8 位随机字符串）。"""
    return f"user_{secrets.token_hex(4)}"


async def register_user(
    email: str,
    password: str,
    display_name: str,
    db: AsyncSession,
    username: Optional[str] = None,
) -> User:
    """注册新用户（Pending 状态）。

    用户名可选，留空自动随机生成。

    Raises:
        ValueError: 邮箱已存在。
    """
    # 邮箱唯一性校验
    exists = await db.execute(select(User).where(User.email == email))
    if exists.scalar_one_or_none():
        raise ValueError("该邮箱已被注册")
    # 用户名：指定或自动生成
    if not username:
        username = _random_username()
    user = User(
        id=str(uuid.uuid4()),
        username=username,
        email=email,
        hashed_password=hash_password(password),
        display_name=display_name or username,
        role_code="pending",
        is_active=False,
        can_create_account=False,
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.commit()
    return user

"""用户注册服务。

完成注册流程：校验唯一性 → 哈希密码 → 创建用户 →
自动创建账户 → 绑定 owner 成员关系 → 初始化默认限额。
"""

import secrets
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.account import Account
from app.models.account_member import AccountMember
from app.services.crypto.hasher import hash_password
from .name_validator import (
    validate_username_format,
    is_name_reserved,
)

# 默认限额键列表
_DEFAULT_QUOTAS = [
    ("max_clients", 50),
    ("max_bandwidth_mb", 1024),
    ("feature.ota", 1),
    ("feature.audit", 1),
]


async def register_user(
    username: str,
    email: str,
    password: str,
    display_name: str,
    db: AsyncSession,
) -> User:
    """注册新用户并自动创建关联账户。

    Raises:
        ValueError: 用户名/邮箱非法或已存在。
    """
    # 格式校验
    if not validate_username_format(username):
        raise ValueError("用户名格式不合法（3~64位小写字母数字下划线）")
    if await is_name_reserved(username, db):
        raise ValueError("该用户名为系统保留名称")
    # 唯一性校验
    await _check_unique(username, email, db)
    # 创建用户
    user = User(
        id=str(uuid.uuid4()),
        username=username,
        email=email,
        hashed_password=hash_password(password),
        display_name=display_name or username,
        role_code="normal",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    # 自动创建账户
    await _create_default_account(user, db)
    await db.commit()
    return user


async def _check_unique(username: str, email: str, db: AsyncSession) -> None:
    """校验用户名和邮箱的全局唯一性。"""
    exists = await db.execute(
        select(User).where((User.username == username) | (User.email == email))
    )
    if exists.scalar_one_or_none():
        raise ValueError("用户名或邮箱已被注册")


async def _create_default_account(user: User, db: AsyncSession) -> None:
    """为新用户创建默认个人账户并绑定 owner 角色。"""
    from app.models.account_quota import AccountQuota

    now = datetime.now(timezone.utc)
    slug = user.username.replace("_", "-")
    account = Account(
        id=str(uuid.uuid4()),
        name=f"{user.display_name} 的账户",
        slug=slug,
        api_key=secrets.token_urlsafe(32),
        is_active=True,
        created_at=now,
    )
    db.add(account)
    # 绑定 owner 成员关系
    member = AccountMember(
        id=str(uuid.uuid4()),
        user_id=user.id,
        account_id=account.id,
        role_in_account="owner",
        joined_at=now,
    )
    db.add(member)
    # 初始化默认限额
    for key, val in _DEFAULT_QUOTAS:
        db.add(
            AccountQuota(
                id=str(uuid.uuid4()),
                account_id=account.id,
                quota_key=key,
                max_value=val,
            )
        )

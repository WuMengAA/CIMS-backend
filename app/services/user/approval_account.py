"""用户审核服务 — 默认账户创建。

为新用户创建默认个人账户、绑定 owner 和初始化限额。
"""

import secrets
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.account import Account
from app.models.account_member import AccountMember
from app.models.account_quota import AccountQuota

# 默认限额键列表
_DEFAULT_QUOTAS = [
    ("max_clients", 50),
    ("max_bandwidth_mb", 1024),
    ("feature.ota", 1),
    ("feature.audit", 1),
]


async def _create_default_account(user: User, db: AsyncSession) -> None:
    """为新用户创建默认个人账户并绑定 owner 角色。"""
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

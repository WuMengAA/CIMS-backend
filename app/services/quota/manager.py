"""限额配置管理服务。

提供超级管理员设置账户限额上限的功能，
支持查询、设置和重置操作。
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account_quota import AccountQuota


async def get_quotas(account_id: str, db: AsyncSession) -> list[AccountQuota]:
    """查询账户的所有限额配置。"""
    result = await db.execute(
        select(AccountQuota).where(AccountQuota.account_id == account_id)
    )
    return list(result.scalars().all())


async def set_quota(
    account_id: str,
    quota_key: str,
    max_value: int,
    db: AsyncSession,
) -> AccountQuota:
    """设置或更新账户的限额上限。"""
    result = await db.execute(
        select(AccountQuota).where(
            AccountQuota.account_id == account_id,
            AccountQuota.quota_key == quota_key,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.max_value = max_value
        await db.commit()
        return existing
    quota = AccountQuota(
        id=str(uuid.uuid4()),
        account_id=account_id,
        quota_key=quota_key,
        max_value=max_value,
    )
    db.add(quota)
    await db.commit()
    return quota

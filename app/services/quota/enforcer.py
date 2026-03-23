"""限额检查与扣减服务。

对指定账户的资源配额进行检查和递增操作，
超限时拒绝并抛出异常。
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account_quota import AccountQuota


async def check_quota(
    account_id: str,
    quota_key: str,
    db: AsyncSession,
) -> bool:
    """检查账户是否在指定配额的限额内。

    Returns:
        True 表示未超限（允许操作），False 表示已达上限。
    """
    quota = await _get_quota(account_id, quota_key, db)
    if not quota:
        return True  # 未配置限额视为无限制
    if quota.max_value == -1:
        return True  # -1 表示无限制
    return quota.current_value < quota.max_value


async def increment_quota(
    account_id: str,
    quota_key: str,
    db: AsyncSession,
    *,
    amount: int = 1,
) -> bool:
    """递增配额使用量。超限时返回 False。

    Args:
        amount: 递增量，默认 1。

    Returns:
        True 表示递增成功，False 表示已超限。
    """
    quota = await _get_quota(account_id, quota_key, db)
    if not quota:
        return True
    if quota.max_value != -1:
        if quota.current_value + amount > quota.max_value:
            return False
    quota.current_value += amount
    await db.commit()
    return True


async def _get_quota(
    account_id: str, key: str, db: AsyncSession
) -> AccountQuota | None:
    """查询指定账户的配额记录。"""
    result = await db.execute(
        select(AccountQuota).where(
            AccountQuota.account_id == account_id,
            AccountQuota.quota_key == key,
        )
    )
    return result.scalar_one_or_none()

"""权限授予与撤销服务。

对 AccountMember 的指定权限进行显式授予或撤销，
实现超细粒度的原子级权限控制。
"""

import uuid

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.member_permission import MemberPermission


async def grant_permission(
    member_id: str,
    permission_code: str,
    db: AsyncSession,
    *,
    granted: bool = True,
) -> MemberPermission:
    """为成员授予（或显式拒绝）某项权限。

    若已有覆盖记录，更新其 granted 状态。
    """
    result = await db.execute(
        select(MemberPermission).where(
            MemberPermission.member_id == member_id,
            MemberPermission.permission_code == permission_code,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.granted = granted
        await db.commit()
        return existing
    perm = MemberPermission(
        id=str(uuid.uuid4()),
        member_id=member_id,
        permission_code=permission_code,
        granted=granted,
    )
    db.add(perm)
    await db.commit()
    return perm


async def revoke_permission(
    member_id: str,
    permission_code: str,
    db: AsyncSession,
) -> bool:
    """撤销成员的某项权限覆盖记录。

    Returns:
        True 表示成功删除，False 表示记录不存在。
    """
    result = await db.execute(
        delete(MemberPermission).where(
            MemberPermission.member_id == member_id,
            MemberPermission.permission_code == permission_code,
        )
    )
    await db.commit()
    return result.rowcount > 0

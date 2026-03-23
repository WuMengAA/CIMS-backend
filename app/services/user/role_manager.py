"""角色分级管理服务。

提供自定义角色的 CRUD 操作和用户角色变更功能，
系统内置角色不可删除。仅超级管理员可执行。
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.custom_role import CustomRole

# 系统内置角色初始数据
SYSTEM_ROLES = [
    ("banned", "已封禁", -1),
    ("pending", "待激活", 0),
    ("normal", "普通用户", 10),
    ("admin", "管理员", 90),
    ("superadmin", "超级管理员", 100),
]


async def ensure_system_roles(db: AsyncSession) -> None:
    """确保系统内置角色存在（幂等操作）。"""
    for code, label, priority in SYSTEM_ROLES:
        exists = await db.execute(select(CustomRole).where(CustomRole.code == code))
        if exists.scalar_one_or_none():
            continue
        db.add(
            CustomRole(
                code=code,
                label=label,
                priority=priority,
                is_system=True,
            )
        )
    await db.commit()


async def list_roles(db: AsyncSession) -> list[CustomRole]:
    """查询所有角色，按优先级降序排列。"""
    result = await db.execute(select(CustomRole).order_by(CustomRole.priority.desc()))
    return list(result.scalars().all())


async def create_role(
    code: str, label: str, priority: int, db: AsyncSession
) -> CustomRole:
    """创建自定义角色。"""
    role = CustomRole(code=code, label=label, priority=priority, is_system=False)
    db.add(role)
    await db.commit()
    return role


async def delete_role(code: str, db: AsyncSession) -> Optional[str]:
    """删除自定义角色。系统角色不可删除。

    Returns:
        错误信息字符串，成功时返回 None。
    """
    result = await db.execute(select(CustomRole).where(CustomRole.code == code))
    role = result.scalar_one_or_none()
    if not role:
        return "角色不存在"
    if role.is_system:
        return "系统内置角色不可删除"
    await db.delete(role)
    await db.commit()
    return None

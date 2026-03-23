"""原子权限检查器。

给定 user_id + account_id + permission_code，
优先查 MemberPermission 覆盖记录，
无覆盖时回退到账户内角色的默认权限集。
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account_member import AccountMember
from app.models.member_permission import MemberPermission

# 账户内角色的默认权限矩阵
_ROLE_DEFAULTS: dict[str, set[str]] = {
    "owner": {
        "client.read",
        "client.write",
        "client.delete",
        "command.execute",
        "config.read",
        "config.write",
        "audit.read",
        "account.manage",
        "member.manage",
    },
    "admin": {
        "client.read",
        "client.write",
        "client.delete",
        "command.execute",
        "config.read",
        "config.write",
        "audit.read",
        "member.manage",
    },
    "member": {
        "client.read",
        "client.write",
        "command.execute",
        "config.read",
    },
    "viewer": {"client.read", "config.read"},
}


async def check_permission(
    user_id: str,
    account_id: str,
    code: str,
    db: AsyncSession,
) -> bool:
    """检查用户在指定账户中是否拥有某权限。

    优先级：显式覆盖 > 角色默认权限。
    """
    # 查找成员关系
    member = await _get_member(user_id, account_id, db)
    if not member:
        return False
    # 查找显式权限覆盖
    override = await _get_override(member.id, code, db)
    if override is not None:
        return override.granted
    # 回退到角色默认权限
    defaults = _ROLE_DEFAULTS.get(member.role_in_account, set())
    return code in defaults


async def _get_member(
    user_id: str, account_id: str, db: AsyncSession
) -> AccountMember | None:
    """查询成员关系记录。"""
    result = await db.execute(
        select(AccountMember).where(
            AccountMember.user_id == user_id,
            AccountMember.account_id == account_id,
        )
    )
    return result.scalar_one_or_none()


async def _get_override(
    member_id: str, code: str, db: AsyncSession
) -> MemberPermission | None:
    """查询成员级别的权限覆盖记录。"""
    result = await db.execute(
        select(MemberPermission).where(
            MemberPermission.member_id == member_id,
            MemberPermission.permission_code == code,
        )
    )
    return result.scalar_one_or_none()

"""权限检查与授予/撤销测试。

测试角色默认权限、显式权限覆盖、跨账户隔离和权限撤销。
"""

import uuid
import pytest
import pytest_asyncio
from datetime import datetime, timezone

from app.models.engine import AsyncSessionLocal
from app.models.account_member import AccountMember
from app.services.permission.checker import check_permission
from app.services.permission.grants import (
    grant_permission,
    revoke_permission,
)
from sqlalchemy import delete


@pytest_asyncio.fixture()
async def member_in_account(test_account):
    """创建测试成员关系。"""
    mid = str(uuid.uuid4())
    uid = f"perm-test-user-{uuid.uuid4().hex[:8]}"
    async with AsyncSessionLocal() as db:
        db.add(
            AccountMember(
                id=mid,
                user_id=uid,
                account_id=test_account,
                role_in_account="member",
                joined_at=datetime.now(timezone.utc),
            )
        )
        await db.commit()
    yield uid, test_account, mid
    async with AsyncSessionLocal() as db:
        await db.execute(delete(AccountMember).where(AccountMember.id == mid))
        await db.commit()


@pytest.mark.asyncio
async def test_member_default_permissions(member_in_account):
    """member 角色应有默认的 client.read 权限。"""
    uid, aid, _ = member_in_account
    async with AsyncSessionLocal() as db:
        assert await check_permission(uid, aid, "client.read", db)
        assert await check_permission(uid, aid, "command.execute", db)
        # member 不应有 account.manage
        assert not await check_permission(uid, aid, "account.manage", db)


@pytest.mark.asyncio
async def test_explicit_grant_overrides(member_in_account):
    """显式授予权限应覆盖角色默认值。"""
    uid, aid, mid = member_in_account
    async with AsyncSessionLocal() as db:
        # member 默认无 account.manage
        assert not await check_permission(uid, aid, "account.manage", db)
        # 显式授予
        await grant_permission(mid, "account.manage", db, granted=True)
        assert await check_permission(uid, aid, "account.manage", db)


@pytest.mark.asyncio
async def test_explicit_deny_overrides(member_in_account):
    """显式拒绝应覆盖角色默认权限。"""
    uid, aid, mid = member_in_account
    async with AsyncSessionLocal() as db:
        assert await check_permission(uid, aid, "client.read", db)
        # 显式拒绝
        await grant_permission(mid, "client.read", db, granted=False)
        assert not await check_permission(uid, aid, "client.read", db)


@pytest.mark.asyncio
async def test_revoke_restores_default(member_in_account):
    """撤销覆盖后应恢复角色默认权限。"""
    uid, aid, mid = member_in_account
    async with AsyncSessionLocal() as db:
        await grant_permission(mid, "client.read", db, granted=False)
        assert not await check_permission(uid, aid, "client.read", db)
        # 撤销覆盖
        result = await revoke_permission(mid, "client.read", db)
        assert result is True
        assert await check_permission(uid, aid, "client.read", db)


@pytest.mark.asyncio
async def test_cross_account_isolation():
    """不同账户之间的权限完全隔离。"""
    uid = f"cross-test-{uuid.uuid4().hex[:8]}"
    aid1 = f"acct1-{uuid.uuid4().hex[:8]}"
    aid2 = f"acct2-{uuid.uuid4().hex[:8]}"
    mid1 = str(uuid.uuid4())
    async with AsyncSessionLocal() as db:
        # 用户仅在 aid1 中是 owner
        db.add(
            AccountMember(
                id=mid1,
                user_id=uid,
                account_id=aid1,
                role_in_account="owner",
                joined_at=datetime.now(timezone.utc),
            )
        )
        await db.commit()
        # 在 aid1 中有全部权限
        assert await check_permission(uid, aid1, "account.manage", db)
        # 在 aid2 中无任何权限
        assert not await check_permission(uid, aid2, "account.manage", db)
        assert not await check_permission(uid, aid2, "client.read", db)
        # 清理
        await db.execute(delete(AccountMember).where(AccountMember.id == mid1))
        await db.commit()

"""多租户隔离测试。

验证不同账户之间的数据和会话完全隔离。
"""

import pytest
import uuid
from tests.mock_client import MockClassIslandClient
from app.grpc.session.manager import SessionManager
from app.models.engine import AsyncSessionLocal
from sqlalchemy import delete

_T1 = "isolation-tenant-1"
_T2 = "isolation-tenant-2"


@pytest.fixture()
def session_mgr():
    """创建测试会话管理器。"""
    return SessionManager()


@pytest.mark.asyncio
async def test_session_tenant_isolation(session_mgr):
    """不同租户的会话 ID 不能互相验证。"""
    c1 = MockClassIslandClient(_T1)
    c2 = MockClassIslandClient(_T2)
    # 两个客户端分别存储握手令牌
    await session_mgr.store_pending_handshake(_T1, c1.uid, b"ch1")
    await session_mgr.store_pending_handshake(_T2, c2.uid, b"ch2")
    # 完成各自握手
    s1 = await session_mgr.complete_handshake(_T1, c1.uid, True)
    s2 = await session_mgr.complete_handshake(_T2, c2.uid, True)
    assert s1 != s2
    # 验证 session 绑定到正确租户
    t1 = await session_mgr.get_session_tenant(s1)
    t2 = await session_mgr.get_session_tenant(s2)
    assert t1 == _T1
    assert t2 == _T2


@pytest.mark.asyncio
async def test_online_status_isolation(session_mgr):
    """租户 A 的在线客户端不会出现在租户 B 的状态列表中。"""
    c1 = MockClassIslandClient(_T1)
    c2 = MockClassIslandClient(_T2)
    await session_mgr.set_client_online(_T1, c1.uid, "10.0.0.1")
    await session_mgr.set_client_online(_T2, c2.uid, "10.0.0.2")
    # 获取各租户状态
    s1 = await session_mgr.get_all_clients_status(_T1)
    s2 = await session_mgr.get_all_clients_status(_T2)
    uids_1 = {s.get("cuid", "") for s in s1}
    uids_2 = {s.get("cuid", "") for s in s2}
    # 互不包含
    assert c2.uid not in uids_1
    assert c1.uid not in uids_2
    # 清理
    await session_mgr.set_client_offline(_T1, c1.uid)
    await session_mgr.set_client_offline(_T2, c2.uid)


@pytest.mark.asyncio
async def test_cross_tenant_handshake_fails(session_mgr):
    """用租户 A 的待定握手不能用租户 B 完成。"""
    uid = str(uuid.uuid4())
    await session_mgr.store_pending_handshake(_T1, uid, b"secret")
    # 用 T2 尝试完成
    result = await session_mgr.complete_handshake(_T2, uid, True)
    assert result is None
    # T1 仍然可以正常完成
    result = await session_mgr.complete_handshake(_T1, uid, True)
    assert result is not None


@pytest.mark.asyncio
async def test_heartbeat_tenant_isolation(session_mgr):
    """心跳只影响对应租户的在线状态。"""
    uid = str(uuid.uuid4())
    await session_mgr.set_client_online(_T1, uid, "10.0.0.1")
    # T1 上线
    assert await session_mgr.is_client_online(_T1, uid)
    # T2 不在线
    assert not await session_mgr.is_client_online(_T2, uid)
    # 清理
    await session_mgr.set_client_offline(_T1, uid)


@pytest.mark.asyncio
async def test_permission_cross_account_members():
    """跨账户成员资格不互通。"""
    from app.services.permission.checker import check_permission
    from app.models.account_member import AccountMember
    from datetime import datetime, timezone

    uid = f"cross-perm-{uuid.uuid4().hex[:8]}"
    aid1 = f"perm-acct-1-{uuid.uuid4().hex[:8]}"
    aid2 = f"perm-acct-2-{uuid.uuid4().hex[:8]}"
    mid = str(uuid.uuid4())
    async with AsyncSessionLocal() as db:
        db.add(
            AccountMember(
                id=mid,
                user_id=uid,
                account_id=aid1,
                role_in_account="admin",
                joined_at=datetime.now(timezone.utc),
            )
        )
        await db.commit()
        # aid1 有权限
        assert await check_permission(uid, aid1, "client.read", db)
        # aid2 无任何权限
        assert not await check_permission(uid, aid2, "client.read", db)
        assert not await check_permission(uid, aid2, "account.manage", db)
        # 清理
        await db.execute(delete(AccountMember).where(AccountMember.id == mid))
        await db.commit()

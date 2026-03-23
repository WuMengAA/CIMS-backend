"""客户端生命周期测试。

模拟 ClassIsland 客户端的完整注册→握手→上报→离线流程。
"""

import pytest
import pytest_asyncio
from tests.mock_client import MockClassIslandClient
from app.grpc.session.manager import SessionManager
from app.models.engine import AsyncSessionLocal
from app.models.database import ClientRecord
from sqlalchemy import select, delete

_TID = "test-account-00000000"


@pytest.fixture()
def session_mgr():
    """创建测试用会话管理器。"""
    return SessionManager()


@pytest_asyncio.fixture(autouse=True)
async def _ensure_client_table():
    """确保租户 Schema 中有 client_records 表。"""
    from app.core.tenant.context import set_search_path

    async with AsyncSessionLocal() as db:
        await set_search_path(db)
    yield


@pytest.mark.asyncio
async def test_register_new_client(session_mgr):
    """全新客户端注册应成功。"""
    client = MockClassIslandClient(_TID)
    rsp = await client.register(session_mgr)
    assert rsp.ServerPublicKey
    # 验证数据库记录
    async with AsyncSessionLocal() as db:
        from app.core.tenant.context import set_search_path

        await set_search_path(db)
        r = await db.execute(select(ClientRecord).where(ClientRecord.uid == client.uid))
        assert r.scalar_one_or_none() is not None
        # 清理
        await db.execute(delete(ClientRecord).where(ClientRecord.uid == client.uid))
        await db.commit()


@pytest.mark.asyncio
async def test_register_updates_mac(session_mgr):
    """重复注册应更新 MAC 地址。"""
    client = MockClassIslandClient(_TID)
    await client.register(session_mgr)
    # 更换 MAC 再注册
    client.mac = "FF:FF:FF:FF:FF:FF"
    await client.register(session_mgr)
    async with AsyncSessionLocal() as db:
        from app.core.tenant.context import set_search_path

        await set_search_path(db)
        r = await db.execute(select(ClientRecord).where(ClientRecord.uid == client.uid))
        record = r.scalar_one()
        assert record.mac == "FF:FF:FF:FF:FF:FF"
        await db.execute(delete(ClientRecord).where(ClientRecord.uid == client.uid))
        await db.commit()


@pytest.mark.asyncio
async def test_handshake_unregistered_client(session_mgr):
    """未注册客户端握手应返回 ClientNotFound。"""
    client = MockClassIslandClient(_TID, uid="unregistered-uid")
    rsp = await client.begin_handshake(session_mgr)
    from app.grpc.api.Protobuf.Enum import Retcode_pb2

    assert rsp.Retcode == Retcode_pb2.ClientNotFound


@pytest.mark.asyncio
async def test_full_lifecycle(session_mgr):
    """完整生命周期：注册→握手存储→完成握手→上线→上报→离线。"""
    client = MockClassIslandClient(_TID)
    # 注册
    await client.register(session_mgr)
    # 存储握手挑战
    await session_mgr.store_pending_handshake(_TID, client.uid, b"test_challenge")
    # 完成握手
    sid = await client.complete_handshake(session_mgr)
    assert sid is not None
    client.session_id = sid
    # 上线
    await session_mgr.set_client_online(_TID, client.uid, "127.0.0.1")
    assert await session_mgr.is_client_online(_TID, client.uid)
    # 上报配置
    rsp = await client.upload_config(session_mgr, '{"test": true}')
    from app.grpc.api.Protobuf.Enum import Retcode_pb2

    assert rsp.Retcode == Retcode_pb2.Success
    # 离线
    await client.go_offline(session_mgr)
    assert not await session_mgr.is_client_online(_TID, client.uid)
    # 清理
    async with AsyncSessionLocal() as db:
        from app.core.tenant.context import set_search_path

        await set_search_path(db)
        await db.execute(delete(ClientRecord).where(ClientRecord.uid == client.uid))
        await db.commit()


@pytest.mark.asyncio
async def test_upload_invalid_session(session_mgr):
    """无效 session 的配置上报应被拒绝。"""
    client = MockClassIslandClient(_TID)
    client.session_id = "invalid-session-id"
    rsp = await client.upload_config(session_mgr, "{}")
    from app.grpc.api.Protobuf.Enum import Retcode_pb2

    assert rsp.Retcode == Retcode_pb2.InvalidRequest


@pytest.mark.asyncio
async def test_multiple_clients_concurrent(session_mgr):
    """多客户端并发注册和握手。"""
    clients = [MockClassIslandClient(_TID) for _ in range(5)]
    # 全部注册
    for c in clients:
        await c.register(session_mgr)
    # 全部存储握手并完成
    for c in clients:
        await session_mgr.store_pending_handshake(
            _TID, c.uid, b"ch_" + c.uid[:4].encode()
        )
        sid = await c.complete_handshake(session_mgr)
        assert sid is not None
    # 全部上线
    for c in clients:
        await session_mgr.set_client_online(_TID, c.uid)
    # 检查状态
    status = await session_mgr.get_all_clients_status(_TID)
    online_count = sum(1 for s in status if s.get("status") == "online")
    assert online_count >= 5
    # 清理
    async with AsyncSessionLocal() as db:
        from app.core.tenant.context import set_search_path

        await set_search_path(db)
        for c in clients:
            await db.execute(delete(ClientRecord).where(ClientRecord.uid == c.uid))
        await db.commit()

import pytest
import asyncio
import grpc
from unittest.mock import MagicMock, AsyncMock

from app.grpc.server import (
    HandshakeServicer,
    ClientRegisterServicer,
    ClientCommandDeliverServicer,
    ConfigUploadServicer,
    AuditServicer,
)
from app.grpc.session_manager import SessionManager
from app.grpc.api.Protobuf.Client import (
    ClientRegisterCsReq_pb2,
    ClientCommandDeliverScReq_pb2,
    HandshakeScReq_pb2,
    ConfigUploadScReq_pb2,
    AuditScReq_pb2,
)
from app.grpc.api.Protobuf.Server import ClientCommandDeliverScRsp_pb2
from app.grpc.api.Protobuf.Enum import Retcode_pb2, CommandTypes_pb2, AuditEvents_pb2
from app.core.tenant import tenant_ctx

from tests.conftest import TEST_TENANT_ID


@pytest.fixture
def session_manager():
    return SessionManager()


@pytest.fixture
def mock_context():
    ctx = MagicMock(spec=grpc.aio.ServicerContext)
    ctx.invocation_metadata.return_value = [("cuid", "test-uid"), ("session", "")]
    ctx.peer.return_value = "ipv4:127.0.0.1:12345"
    ctx.abort = AsyncMock()
    return ctx


# ===========================================================================
# Session Manager Tests (all async now — uses Redis)
# ===========================================================================


def test_session_manager_key_generation(session_manager):
    assert session_manager.public_key_armor.startswith(
        "-----BEGIN PGP PUBLIC KEY BLOCK-----"
    )


@pytest.mark.asyncio
async def test_session_manager_handshake_lifecycle(session_manager):
    tid = TEST_TENANT_ID

    await session_manager.store_pending_handshake(tid, "client-1", "token-abc")
    sid = await session_manager.complete_handshake(tid, "client-1", accepted=True)
    assert sid is not None

    cuid = await session_manager.validate_session(sid)
    assert cuid == "client-1"

    # Sessions expire via Redis TTL; verify tenant lookup works
    tenant = await session_manager.get_session_tenant(sid)
    assert tenant == tid


@pytest.mark.asyncio
async def test_session_manager_handshake_rejection(session_manager):
    tid = TEST_TENANT_ID
    await session_manager.store_pending_handshake(tid, "client-2", "token-xyz")
    sid = await session_manager.complete_handshake(tid, "client-2", accepted=False)
    assert sid is None


@pytest.mark.asyncio
async def test_session_manager_handshake_no_pending(session_manager):
    tid = TEST_TENANT_ID
    sid = await session_manager.complete_handshake(tid, "nonexistent", accepted=True)
    assert sid is None


@pytest.mark.asyncio
async def test_session_manager_client_online_status(session_manager):
    tid = TEST_TENANT_ID
    await session_manager.set_client_online(tid, "c1", ip="1.2.3.4")
    assert await session_manager.is_client_online(tid, "c1") is True

    statuses = await session_manager.get_all_clients_status(tid)
    assert len(statuses) >= 1
    found = [s for s in statuses if s["uid"] == "c1"]
    assert len(found) == 1

    await session_manager.update_heartbeat(tid, "c1")
    await session_manager.set_client_offline(tid, "c1")
    assert await session_manager.is_client_online(tid, "c1") is False


def test_session_manager_decrypt_challenge(session_manager):
    import pgpy

    pub_key, _ = pgpy.PGPKey.from_blob(session_manager.public_key_armor)
    token = "test-challenge-token-12345"
    msg = pgpy.PGPMessage.new(token)
    encrypted = pub_key.encrypt(msg)

    decrypted = session_manager.decrypt_challenge(str(encrypted))
    assert decrypted == token


def test_session_manager_decrypt_invalid(session_manager):
    result = session_manager.decrypt_challenge("not-a-valid-pgp-message")
    assert result is None


# ===========================================================================
# ClientRegister Service Tests
# ===========================================================================


@pytest.mark.asyncio
async def test_client_register(session_manager, mock_context):
    # Set tenant context
    token = tenant_ctx.set(TEST_TENANT_ID)
    try:
        servicer = ClientRegisterServicer(session_manager)
        req = ClientRegisterCsReq_pb2.ClientRegisterCsReq(
            ClientUid="test-uid", ClientId="class-1", ClientMac="AABBCCDDEEFF"
        )

        rsp = await servicer.Register(req, mock_context)
        assert rsp.Retcode == Retcode_pb2.Registered
        assert rsp.ServerPublicKey.startswith("-----BEGIN PGP PUBLIC KEY BLOCK-----")

        # Register again (upsert)
        rsp2 = await servicer.Register(req, mock_context)
        assert rsp2.Retcode == Retcode_pb2.Registered

        # Unregister
        rsp_unreg = await servicer.UnRegister(req, mock_context)
        assert rsp_unreg.Retcode == Retcode_pb2.Success
    finally:
        tenant_ctx.reset(token)


# ===========================================================================
# Handshake Service Tests
# ===========================================================================


@pytest.mark.asyncio
async def test_handshake_full_flow(session_manager, mock_context):
    token = tenant_ctx.set(TEST_TENANT_ID)
    try:
        register_servicer = ClientRegisterServicer(session_manager)
        await register_servicer.Register(
            ClientRegisterCsReq_pb2.ClientRegisterCsReq(
                ClientUid="hs-uid", ClientId="class-2", ClientMac="112233445566"
            ),
            mock_context,
        )

        import pgpy

        pub_key, _ = pgpy.PGPKey.from_blob(session_manager.public_key_armor)
        challenge = "my-challenge-token"
        msg = pgpy.PGPMessage.new(challenge)
        encrypted = str(pub_key.encrypt(msg))

        handshake_servicer = HandshakeServicer(session_manager)

        begin_req = HandshakeScReq_pb2.HandshakeScBeginHandShakeReq(
            ClientUid="hs-uid",
            ClientMac="112233445566",
            ChallengeTokenEncrypted=encrypted,
            RequestedServerKeyId=0,
        )
        begin_rsp = await handshake_servicer.BeginHandshake(begin_req, mock_context)
        assert begin_rsp.Retcode == Retcode_pb2.Success
        assert begin_rsp.ChallengeTokenDecrypted == challenge

        mock_context.invocation_metadata.return_value = [("cuid", "hs-uid")]
        complete_req = HandshakeScReq_pb2.HandshakeScCompleteHandshakeReq(Accepted=True)
        complete_rsp = await handshake_servicer.CompleteHandshake(
            complete_req, mock_context
        )
        assert complete_rsp.Retcode == Retcode_pb2.Success
        assert len(complete_rsp.SessionId) > 0
    finally:
        tenant_ctx.reset(token)


@pytest.mark.asyncio
async def test_handshake_unregistered_client(session_manager, mock_context):
    token = tenant_ctx.set(TEST_TENANT_ID)
    try:
        handshake_servicer = HandshakeServicer(session_manager)
        begin_req = HandshakeScReq_pb2.HandshakeScBeginHandShakeReq(
            ClientUid="unknown-uid",
            ClientMac="000000000000",
            ChallengeTokenEncrypted="",
        )
        rsp = await handshake_servicer.BeginHandshake(begin_req, mock_context)
        assert rsp.Retcode == Retcode_pb2.ClientNotFound
    finally:
        tenant_ctx.reset(token)


@pytest.mark.asyncio
async def test_handshake_mac_mismatch(session_manager, mock_context):
    token = tenant_ctx.set(TEST_TENANT_ID)
    try:
        register_servicer = ClientRegisterServicer(session_manager)
        await register_servicer.Register(
            ClientRegisterCsReq_pb2.ClientRegisterCsReq(
                ClientUid="mac-uid", ClientId="class-3", ClientMac="AABBCCDDEEFF"
            ),
            mock_context,
        )

        handshake_servicer = HandshakeServicer(session_manager)
        begin_req = HandshakeScReq_pb2.HandshakeScBeginHandShakeReq(
            ClientUid="mac-uid",
            ClientMac="000000000000",
            ChallengeTokenEncrypted="",
        )
        rsp = await handshake_servicer.BeginHandshake(begin_req, mock_context)
        assert rsp.Retcode == Retcode_pb2.InvalidRequest
    finally:
        tenant_ctx.reset(token)


@pytest.mark.asyncio
async def test_handshake_client_rejects(session_manager, mock_context):
    token = tenant_ctx.set(TEST_TENANT_ID)
    try:
        register_servicer = ClientRegisterServicer(session_manager)
        await register_servicer.Register(
            ClientRegisterCsReq_pb2.ClientRegisterCsReq(
                ClientUid="rej-uid", ClientId="", ClientMac="AABBCCDDEEFF"
            ),
            mock_context,
        )

        import pgpy

        pub_key, _ = pgpy.PGPKey.from_blob(session_manager.public_key_armor)
        msg = pgpy.PGPMessage.new("token")
        encrypted = str(pub_key.encrypt(msg))

        hs = HandshakeServicer(session_manager)
        await hs.BeginHandshake(
            HandshakeScReq_pb2.HandshakeScBeginHandShakeReq(
                ClientUid="rej-uid",
                ClientMac="AABBCCDDEEFF",
                ChallengeTokenEncrypted=encrypted,
            ),
            mock_context,
        )

        mock_context.invocation_metadata.return_value = [("cuid", "rej-uid")]
        rsp = await hs.CompleteHandshake(
            HandshakeScReq_pb2.HandshakeScCompleteHandshakeReq(Accepted=False),
            mock_context,
        )
        assert rsp.Retcode == Retcode_pb2.HandshakeClientRejected
    finally:
        tenant_ctx.reset(token)


# ===========================================================================
# ClientCommandDeliver Tests
# ===========================================================================


@pytest.mark.asyncio
async def test_client_command_deliver_missing_cuid(session_manager):
    token = tenant_ctx.set(TEST_TENANT_ID)
    try:
        servicer = ClientCommandDeliverServicer(session_manager)
        ctx = MagicMock(spec=grpc.aio.ServicerContext)
        ctx.invocation_metadata.return_value = []
        ctx.abort = AsyncMock()

        async def req_iterator():
            yield ClientCommandDeliverScReq_pb2.ClientCommandDeliverScReq()

        gen = servicer.ListenCommand(req_iterator(), ctx)
        try:
            async for _ in gen:
                pass
        except StopAsyncIteration:
            pass

        ctx.abort.assert_called_once_with(
            grpc.StatusCode.UNAUTHENTICATED, "Missing 'cuid' in metadata"
        )
    finally:
        tenant_ctx.reset(token)


@pytest.mark.asyncio
async def test_client_command_deliver_ping_pong(session_manager):
    token = tenant_ctx.set(TEST_TENANT_ID)
    try:
        servicer = ClientCommandDeliverServicer(session_manager)
        ctx = MagicMock(spec=grpc.aio.ServicerContext)
        ctx.invocation_metadata.return_value = [("cuid", "pp-uid"), ("session", "")]
        ctx.peer.return_value = "ipv4:127.0.0.1:9999"

        async def req_iterator():
            yield ClientCommandDeliverScReq_pb2.ClientCommandDeliverScReq(
                Type=CommandTypes_pb2.Ping
            )
            await asyncio.sleep(0.1)

        gen = servicer.ListenCommand(req_iterator(), ctx)
        iterator = gen.__aiter__()

        rsp = await asyncio.wait_for(iterator.__anext__(), timeout=2.0)
        assert rsp.Type == CommandTypes_pb2.Pong
        assert rsp.RetCode == Retcode_pb2.Success
    finally:
        tenant_ctx.reset(token)


@pytest.mark.asyncio
async def test_client_command_deliver_send_command(session_manager):
    tid = TEST_TENANT_ID
    token = tenant_ctx.set(tid)
    try:
        servicer = ClientCommandDeliverServicer(session_manager)
        ctx = MagicMock(spec=grpc.aio.ServicerContext)
        ctx.invocation_metadata.return_value = [("cuid", "cmd-uid"), ("session", "")]
        ctx.peer.return_value = "ipv4:127.0.0.1:8888"

        stop_event = asyncio.Event()

        async def req_iterator():
            await stop_event.wait()

        collected = []

        async def run_listener():
            async for resp in servicer.ListenCommand(req_iterator(), ctx):
                collected.append(resp)
                if len(collected) >= 1:
                    stop_event.set()

        listener_task = asyncio.create_task(run_listener())

        queue_key = f"{tid}:cmd-uid"
        for _ in range(50):
            if queue_key in servicer.client_queues:
                break
            await asyncio.sleep(0.01)

        cmd = ClientCommandDeliverScRsp_pb2.ClientCommandDeliverScRsp(
            RetCode=Retcode_pb2.Success,
            Type=CommandTypes_pb2.RestartApp,
        )
        await servicer.send_command(tid, "cmd-uid", cmd)

        try:
            await asyncio.wait_for(listener_task, timeout=3.0)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            pass

        assert len(collected) >= 1
        assert collected[0].Type == CommandTypes_pb2.RestartApp

        # Send to non-existent client
        await servicer.send_command(tid, "missing-uid", cmd)
    finally:
        tenant_ctx.reset(token)


# ===========================================================================
# ConfigUpload Service Tests
# ===========================================================================


@pytest.mark.asyncio
async def test_config_upload(session_manager, mock_context):
    tid = TEST_TENANT_ID
    token = tenant_ctx.set(tid)
    try:
        servicer = ConfigUploadServicer(session_manager)

        await session_manager.store_pending_handshake(tid, "test-uid", "token")
        sid = await session_manager.complete_handshake(tid, "test-uid", accepted=True)
        mock_context.invocation_metadata.return_value = [
            ("cuid", "test-uid"),
            ("session", sid),
        ]

        import uuid

        req = ConfigUploadScReq_pb2.ConfigUploadScReq(
            RequestGuidId=str(uuid.uuid4()),
            Payload='{"settings": "value"}',
        )
        rsp = await servicer.UploadConfig(req, mock_context)
        assert rsp.Retcode == Retcode_pb2.Success
    finally:
        tenant_ctx.reset(token)


@pytest.mark.asyncio
async def test_config_upload_invalid_session(session_manager, mock_context):
    token = tenant_ctx.set(TEST_TENANT_ID)
    try:
        servicer = ConfigUploadServicer(session_manager)
        mock_context.invocation_metadata.return_value = [
            ("cuid", "x"),
            ("session", "invalid"),
        ]

        req = ConfigUploadScReq_pb2.ConfigUploadScReq(
            RequestGuidId="guid-456",
            Payload="{}",
        )
        rsp = await servicer.UploadConfig(req, mock_context)
        assert rsp.Retcode == Retcode_pb2.InvalidRequest
    finally:
        tenant_ctx.reset(token)


# ===========================================================================
# Audit Service Tests
# ===========================================================================


@pytest.mark.asyncio
async def test_audit_log_event(session_manager, mock_context):
    tid = TEST_TENANT_ID
    token = tenant_ctx.set(tid)
    try:
        servicer = AuditServicer(session_manager)

        await session_manager.store_pending_handshake(tid, "test-uid", "token")
        sid = await session_manager.complete_handshake(tid, "test-uid", accepted=True)
        mock_context.invocation_metadata.return_value = [
            ("cuid", "test-uid"),
            ("session", sid),
        ]

        req = AuditScReq_pb2.AuditScReq(
            Event=AuditEvents_pb2.AppStarted,
            Payload=b"\x00\x01\x02",
            TimestampUtc=1700000000,
        )
        rsp = await servicer.LogEvent(req, mock_context)
        assert rsp.Retcode == Retcode_pb2.Success
    finally:
        tenant_ctx.reset(token)


@pytest.mark.asyncio
async def test_audit_invalid_session(session_manager, mock_context):
    token = tenant_ctx.set(TEST_TENANT_ID)
    try:
        servicer = AuditServicer(session_manager)
        mock_context.invocation_metadata.return_value = [
            ("cuid", "x"),
            ("session", "bad"),
        ]

        req = AuditScReq_pb2.AuditScReq(
            Event=AuditEvents_pb2.AppCrashed,
            Payload=b"",
            TimestampUtc=0,
        )
        rsp = await servicer.LogEvent(req, mock_context)
        assert rsp.Retcode == Retcode_pb2.InvalidRequest
    finally:
        tenant_ctx.reset(token)


# ===========================================================================
# Additional Coverage Tests
# ===========================================================================


@pytest.mark.asyncio
async def test_handshake_decrypt_failure(session_manager, mock_context):
    token = tenant_ctx.set(TEST_TENANT_ID)
    try:
        register_servicer = ClientRegisterServicer(session_manager)
        await register_servicer.Register(
            ClientRegisterCsReq_pb2.ClientRegisterCsReq(
                ClientUid="decrypt-fail-uid",
                ClientId="class-x",
                ClientMac="AABBCCDDEEFF",
            ),
            mock_context,
        )

        hs = HandshakeServicer(session_manager)
        begin_req = HandshakeScReq_pb2.HandshakeScBeginHandShakeReq(
            ClientUid="decrypt-fail-uid",
            ClientMac="AABBCCDDEEFF",
            ChallengeTokenEncrypted="not-valid-pgp-data",
        )
        rsp = await hs.BeginHandshake(begin_req, mock_context)
        assert rsp.Retcode == Retcode_pb2.ServerInternalError
    finally:
        tenant_ctx.reset(token)


@pytest.mark.asyncio
async def test_complete_handshake_accepted_no_pending(session_manager, mock_context):
    token = tenant_ctx.set(TEST_TENANT_ID)
    try:
        hs = HandshakeServicer(session_manager)
        mock_context.invocation_metadata.return_value = [("cuid", "no-pending-uid")]
        rsp = await hs.CompleteHandshake(
            HandshakeScReq_pb2.HandshakeScCompleteHandshakeReq(Accepted=True),
            mock_context,
        )
        assert rsp.Retcode == Retcode_pb2.InvalidRequest
    finally:
        tenant_ctx.reset(token)


def test_session_manager_decrypt_no_key():
    sm = SessionManager()
    sm._private_key = None
    result = sm.decrypt_challenge("anything")
    assert result is None


def test_session_manager_generates_new_key(tmp_path):
    import os

    key_path = str(tmp_path / "brand_new.key")
    assert not os.path.exists(key_path)

    sm = SessionManager(key_file=key_path)
    assert os.path.exists(key_path)
    assert sm.public_key_armor.startswith("-----BEGIN PGP PUBLIC KEY BLOCK-----")


def test_session_manager_corrupt_key_file(tmp_path):

    key_path = str(tmp_path / "corrupt.key")
    with open(key_path, "w") as f:
        f.write("this is not a valid PGP key")

    sm = SessionManager(key_file=key_path)
    assert sm.public_key_armor.startswith("-----BEGIN PGP PUBLIC KEY BLOCK-----")

"""模拟 ClassIsland 客户端。

基于上游 gRPC 协议实现完整设备生命周期模拟，
用于生产级测试。
"""

import uuid
from unittest.mock import AsyncMock, MagicMock


class MockClassIslandClient:
    """模拟 ClassIsland 桌面客户端的 gRPC 交互。"""

    def __init__(self, tenant_id: str, uid: str = None):
        """初始化模拟客户端。"""
        self.tenant_id = tenant_id
        self.uid = uid or str(uuid.uuid4())
        self.mac = f"AA:BB:CC:{uuid.uuid4().hex[:2].upper()}"
        self.session_id = None
        self.server_pubkey = None

    async def register(self, session_manager):
        """模拟客户端注册。"""
        from app.grpc.server.register import ClientRegisterServicer

        svc = ClientRegisterServicer(session_manager)
        req = _make_register_req(self.uid, self.mac)
        ctx = _make_context(self.tenant_id)
        rsp = await svc.Register(req, ctx)
        self.server_pubkey = rsp.ServerPublicKey
        return rsp

    async def begin_handshake(self, session_manager):
        """模拟握手开始阶段。"""
        from app.grpc.server.handshake import HandshakeServicer

        svc = HandshakeServicer(session_manager)
        token = b"challenge_" + self.uid.encode()[:8]
        # 使用服务器密钥加密（测试中跳过加密）
        req = _make_handshake_req(self.uid, self.mac, token)
        ctx = _make_context(self.tenant_id)
        return await svc.BeginHandshake(req, ctx)

    async def complete_handshake(self, session_manager):
        """模拟完成握手并获取 session。"""
        sid = await session_manager.complete_handshake(self.tenant_id, self.uid, True)
        self.session_id = sid
        return sid

    async def upload_config(self, session_manager, payload):
        """模拟配置上报。"""
        from app.grpc.server.config_upload import ConfigUploadServicer

        svc = ConfigUploadServicer(session_manager)
        req = _make_upload_req(payload)
        ctx = _make_context(self.tenant_id, session=self.session_id)
        return await svc.UploadConfig(req, ctx)

    async def go_offline(self, session_manager):
        """模拟客户端下线。"""
        await session_manager.set_client_offline(self.tenant_id, self.uid)
        self.session_id = None


def _make_context(tenant_id, session=None):
    """构造模拟 gRPC context。"""
    from app.core.tenant.context import tenant_ctx, schema_ctx

    tenant_ctx.set(tenant_id)
    schema_ctx.set("tenant_test-school")
    ctx = MagicMock()
    md = {":authority": "test-school.localhost"}
    if session:
        md["session"] = session
    ctx.invocation_metadata.return_value = list(md.items())
    ctx.peer.return_value = "ipv4:127.0.0.1:50051"
    ctx.abort = AsyncMock()
    return ctx


def _make_register_req(uid, mac):
    """构造注册请求。"""
    req = MagicMock()
    req.ClientUid = uid
    req.ClientId = f"client-{uid[:8]}"
    req.ClientMac = mac
    return req


def _make_handshake_req(uid, mac, token):
    """构造握手请求。"""
    req = MagicMock()
    req.ClientUid = uid
    req.ClientMac = mac
    req.ChallengeTokenEncrypted = token
    return req


def _make_upload_req(payload):
    """构造配置上报请求。"""
    req = MagicMock()
    req.RequestGuidId = str(uuid.uuid4())
    req.Payload = payload
    return req

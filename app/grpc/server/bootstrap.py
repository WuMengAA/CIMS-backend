"""gRPC 服务器引导。

注册所有 Servicer 并建立异步监听端口。提供系统级的双向流控能力。
"""

import grpc
from app.grpc.session.manager import SessionManager
from app.grpc.api.Protobuf.Service import (
    Handshake_pb2_grpc,
    ClientRegister_pb2_grpc,
    ClientCommandDeliver_pb2_grpc,
    ConfigUpload_pb2_grpc,
    Audit_pb2_grpc,
)
from .handshake import HandshakeServicer
from .register import ClientRegisterServicer
from .command_deliver import ClientCommandDeliverServicer
from .config_upload import ConfigUploadServicer
from .audit import AuditServicer
from app.core.config import GRPC_PORT


async def serve_grpc(interceptors=None):
    """启动全功能多租户 gRPC 服务器实例。"""
    mgr = SessionManager()
    srv = grpc.aio.server(interceptors=interceptors or [])

    # 实例化并注册服务逻辑
    Handshake_pb2_grpc.add_HandshakeServicer_to_server(HandshakeServicer(mgr), srv)
    ClientRegister_pb2_grpc.add_ClientRegisterServicer_to_server(
        ClientRegisterServicer(mgr), srv
    )

    cmd_s = ClientCommandDeliverServicer(mgr)
    ClientCommandDeliver_pb2_grpc.add_ClientCommandDeliverServicer_to_server(cmd_s, srv)
    ConfigUpload_pb2_grpc.add_ConfigUploadServicer_to_server(
        ConfigUploadServicer(mgr), srv
    )
    Audit_pb2_grpc.add_AuditServicer_to_server(AuditServicer(mgr), srv)

    srv.add_insecure_port(f"[::]:{GRPC_PORT}")
    await srv.start()
    return srv, cmd_s, mgr

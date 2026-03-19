"""握手确认与完成。

处理客户端对挑战令牌的最终反馈，并生成有效的 Session ID。
"""

from app.grpc.api.Protobuf.Server import HandshakeScRsp_pb2
from app.grpc.api.Protobuf.Enum import Retcode_pb2
from .helpers import get_metadata_dict, get_tenant_id_safe


async def complete_handshake_logic(servicer, request, context):
    """确定握手细节并颁发 Session ID。"""
    tenant_id = get_tenant_id_safe()
    cuid = get_metadata_dict(context).get("cuid", "")

    session_id = await servicer._sm.complete_handshake(
        tenant_id, cuid, request.Accepted
    )

    if not request.Accepted:
        return HandshakeScRsp_pb2.HandshakeScCompleteHandshakeRsp(
            Retcode=Retcode_pb2.HandshakeClientRejected
        )

    if session_id is None:
        return HandshakeScRsp_pb2.HandshakeScCompleteHandshakeRsp(
            Retcode=Retcode_pb2.InvalidRequest
        )

    return HandshakeScRsp_pb2.HandshakeScCompleteHandshakeRsp(
        Retcode=Retcode_pb2.Success, SessionId=session_id
    )

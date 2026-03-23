"""握手确认与完成。

验证挑战令牌存在性后颁发 Session ID，挑战令牌为一次性使用。
"""

from app.grpc.api.Protobuf.Server import HandshakeScRsp_pb2
from app.grpc.api.Protobuf.Enum import Retcode_pb2
from .helpers import get_metadata_dict, get_tenant_id_safe


async def complete_handshake_logic(servicer, request, context):
    """验证挑战令牌后颁发 Session ID。"""
    tenant_id = get_tenant_id_safe()
    cuid = get_metadata_dict(context).get("cuid", "")

    # 取出存储的挑战令牌（取后即删，保证一次性使用）
    pending = await servicer._sm.pop_handshake_challenge(tenant_id, cuid)

    if not request.Accepted:
        return HandshakeScRsp_pb2.HandshakeScCompleteHandshakeRsp(
            Retcode=Retcode_pb2.HandshakeClientRejected
        )

    # 挑战令牌必须存在且未过期
    if not pending:
        return HandshakeScRsp_pb2.HandshakeScCompleteHandshakeRsp(
            Retcode=Retcode_pb2.InvalidRequest
        )

    session_id = await servicer._sm.create_session(tenant_id, cuid)

    return HandshakeScRsp_pb2.HandshakeScCompleteHandshakeRsp(
        Retcode=Retcode_pb2.Success, SessionId=session_id
    )

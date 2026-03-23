"""Cyrene_MSP 握手服务逻辑。

实现客户端与服务端的挑战-响应机制，用于建立加密的命令会话。
"""

import logging
from sqlalchemy import select

from app.models.database import AsyncSessionLocal, ClientRecord
from app.grpc.api.Protobuf.Client import HandshakeScReq_pb2
from app.grpc.api.Protobuf.Server import HandshakeScRsp_pb2
from app.grpc.api.Protobuf.Enum import Retcode_pb2
from app.grpc.api.Protobuf.Service import Handshake_pb2_grpc
from .helpers import get_tenant_id_safe

logger = logging.getLogger(__name__)


class HandshakeServicer(Handshake_pb2_grpc.HandshakeServicer):
    """管理 Cyrene_MSP 握手协议周期。"""

    def __init__(self, session_manager):
        self._sm = session_manager

    async def BeginHandshake(self, request: HandshakeScReq_pb2, context):
        """开始握手：验证身份并签发解密后的挑战令牌。"""
        tid = get_tenant_id_safe()
        cuid, mac = request.ClientUid, request.ClientMac

        from app.core.tenant.context import set_search_path

        async with AsyncSessionLocal() as db:
            await set_search_path(db)
            stmt = select(ClientRecord).where(ClientRecord.uid == cuid)
            client = (await db.execute(stmt)).scalar_one_or_none()

        if not client:
            return HandshakeScRsp_pb2.HandshakeScBeginHandShakeRsp(
                Retcode=Retcode_pb2.ClientNotFound
            )
        if client.mac and client.mac != mac:
            return HandshakeScRsp_pb2.HandshakeScBeginHandShakeRsp(
                Retcode=Retcode_pb2.InvalidRequest
            )

        decrypted = self._sm.decrypt_challenge(request.ChallengeTokenEncrypted)
        if decrypted is None:
            return HandshakeScRsp_pb2.HandshakeScBeginHandShakeRsp(
                Retcode=Retcode_pb2.ServerInternalError
            )

        await self._sm.store_pending_handshake(tid, cuid, decrypted)
        return HandshakeScRsp_pb2.HandshakeScBeginHandShakeRsp(
            Retcode=Retcode_pb2.Success,
            ChallengeTokenDecrypted=decrypted,
            ServerPublicKey=self._sm.public_key_armor,
        )

    async def CompleteHandshake(self, request, context):
        """确定握手细节并颁发 Session ID。"""
        from .handshake_utils import complete_handshake_logic

        return await complete_handshake_logic(self, request, context)

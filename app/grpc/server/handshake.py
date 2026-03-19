"""Cyrene_MSP 握手服务逻辑。

实现客户端与服务端的挑战-响应机制，用于建立加密的命令会话。
"""

import logging
import grpc
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

    async def BeginHandshake(
        self, request: HandshakeScReq_pb2, context: grpc.aio.ServicerContext
    ):
        """开始握手：验证身份并签发解密后的挑战令牌。"""
        tenant_id = get_tenant_id_safe()
        cuid, mac = request.ClientUid, request.ClientMac

        async with AsyncSessionLocal() as db:
            stmt = select(ClientRecord).where(
                ClientRecord.tenant_id == tenant_id, ClientRecord.uid == cuid
            )
            client = (await db.execute(stmt)).scalar_one_or_none()

        if not client or (client.mac and client.mac != mac):
            return HandshakeScRsp_pb2.HandshakeScBeginHandShakeRsp(
                Retcode=Retcode_pb2.ClientNotFound
            )

        # 解密令牌并存储在 Redis 待确认
        decrypted = self._sm.decrypt_challenge(request.ChallengeTokenEncrypted)
        await self._sm.store_pending_handshake(tenant_id, cuid, decrypted)

        return HandshakeScRsp_pb2.HandshakeScBeginHandShakeRsp(
            Retcode=Retcode_pb2.Success,
            ChallengeTokenDecrypted=decrypted,
            ServerPublicKey=self._sm.public_key_armor,
        )

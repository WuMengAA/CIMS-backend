"""客户端注册服务逻辑。

处理终端设备的初次注册入网请求，并将设备信息持久化到租户下的 SQL 数据库。
"""

import logging
from datetime import datetime, timezone
import grpc
from sqlalchemy import select

from app.models.database import AsyncSessionLocal, ClientRecord
from app.grpc.api.Protobuf.Client import ClientRegisterCsReq_pb2
from app.grpc.api.Protobuf.Server import ClientRegisterScRsp_pb2
from app.grpc.api.Protobuf.Enum import Retcode_pb2
from app.grpc.api.Protobuf.Service import ClientRegister_pb2_grpc
from .helpers import get_tenant_id_safe

logger = logging.getLogger(__name__)


class ClientRegisterServicer(ClientRegister_pb2_grpc.ClientRegisterServicer):
    """管理 Cyrene_MSP 终端注册生命周期。"""

    def __init__(self, session_manager):
        self._sm = session_manager

    async def Register(
        self, request: ClientRegisterCsReq_pb2, context: grpc.aio.ServicerContext
    ):
        """记录新客户端信息或更新现有设备的 MAC 地址。"""
        tid, cuid = get_tenant_id_safe(), request.ClientUid

        async with AsyncSessionLocal() as db:
            stmt = select(ClientRecord).where(
                ClientRecord.tenant_id == tid, ClientRecord.uid == cuid
            )
            record = (await db.execute(stmt)).scalar_one_or_none() or ClientRecord(
                tenant_id=tid, uid=cuid, registered_at=datetime.now(timezone.utc)
            )
            record.client_id, record.mac = request.ClientId, request.ClientMac
            db.add(record)
            await db.commit()

        return ClientRegisterScRsp_pb2.ClientRegisterScRsp(
            Retcode=Retcode_pb2.Registered, ServerPublicKey=self._sm.public_key_armor
        )

    async def UnRegister(self, request, context):
        """从系统中彻底注销设备记录并同步离线状态。"""
        tid, cuid = get_tenant_id_safe(), request.ClientUid
        async with AsyncSessionLocal() as db:
            await db.delete(await db.get(ClientRecord, (tid, cuid)))
            await db.commit()
        await self._sm.set_client_offline(tid, cuid)
        return ClientRegisterScRsp_pb2.ClientRegisterScRsp(Retcode=Retcode_pb2.Success)

"""客户端注册服务逻辑。

处理终端设备注册入网及注销请求。
"""

import logging
from datetime import datetime, timezone
from sqlalchemy import select

from app.models.database import AsyncSessionLocal, ClientRecord
from app.grpc.api.Protobuf.Client import ClientRegisterCsReq_pb2
from app.grpc.api.Protobuf.Server import ClientRegisterScRsp_pb2
from app.grpc.api.Protobuf.Enum import Retcode_pb2
from app.grpc.api.Protobuf.Service import ClientRegister_pb2_grpc
from .unregister import handle_unregister

logger = logging.getLogger(__name__)


class ClientRegisterServicer(ClientRegister_pb2_grpc.ClientRegisterServicer):
    """管理终端注册生命周期。"""

    def __init__(self, session_manager):
        self._sm = session_manager

    async def Register(self, request: ClientRegisterCsReq_pb2, context):
        """记录新客户端信息或更新现有设备的 MAC 地址。"""
        cuid = request.ClientUid
        async with AsyncSessionLocal() as db:
            from app.core.tenant.context import set_search_path

            await set_search_path(db)
            stmt = select(ClientRecord).where(ClientRecord.uid == cuid)
            record = (await db.execute(stmt)).scalar_one_or_none() or ClientRecord(
                uid=cuid, registered_at=datetime.now(timezone.utc)
            )
            record.client_id = request.ClientId
            record.mac = request.ClientMac
            db.add(record)
            await db.commit()
        return ClientRegisterScRsp_pb2.ClientRegisterScRsp(
            Retcode=Retcode_pb2.Registered, ServerPublicKey=self._sm.public_key_armor
        )

    async def UnRegister(self, request, context):
        """验证 session 后注销设备记录（委托至 unregister 模块）。"""
        return await handle_unregister(self._sm, request, context)

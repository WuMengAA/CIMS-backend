"""配置上报服务。

接收客户端通过 gRPC 上传的配置快照，通常由管理端触发 get_config 请求后产生。
"""

from datetime import datetime, timezone
from app.models.database import AsyncSessionLocal, ConfigUploadRecord
from app.grpc.api.Protobuf.Server import ConfigUploadScRsp_pb2
from app.grpc.api.Protobuf.Enum import Retcode_pb2
from app.grpc.api.Protobuf.Service import ConfigUpload_pb2_grpc
from .helpers import get_metadata_dict, get_tenant_id_safe


class ConfigUploadServicer(ConfigUpload_pb2_grpc.ConfigUploadServicer):
    """支持 Cyrene_MSP 异步配置上报流程。"""

    def __init__(self, session_manager):
        self._sm = session_manager

    async def UploadConfig(self, request, context):
        """记录来自特定会话的配置 Payload。"""
        md = get_metadata_dict(context)
        cuid, sid = md.get("cuid", ""), md.get("session", "")

        # 校验会话合法性
        if not await self._sm.validate_session(sid):
            return ConfigUploadScRsp_pb2.ConfigUploadScRsp(
                Retcode=Retcode_pb2.InvalidRequest, Message="会话失效"
            )

        tid = await self._sm.get_session_tenant(sid) or get_tenant_id_safe()

        async with AsyncSessionLocal() as db:
            db.add(
                ConfigUploadRecord(
                    tenant_id=tid,
                    request_guid=request.RequestGuidId,
                    client_uid=cuid,
                    payload=request.Payload,
                    uploaded_at=datetime.now(timezone.utc),
                )
            )
            await db.commit()

        return ConfigUploadScRsp_pb2.ConfigUploadScRsp(
            Retcode=Retcode_pb2.Success, Message="上报成功"
        )

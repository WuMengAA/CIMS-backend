"""配置上报服务。

接收客户端上传的配置快照，从 session 提取可信 cuid。
"""

from datetime import datetime, timezone
from app.models.database import AsyncSessionLocal, ConfigUploadRecord

from app.grpc.api.Protobuf.Server import ConfigUploadScRsp_pb2
from app.grpc.api.Protobuf.Enum import Retcode_pb2
from app.grpc.api.Protobuf.Service import ConfigUpload_pb2_grpc
from .helpers import get_metadata_dict


class ConfigUploadServicer(ConfigUpload_pb2_grpc.ConfigUploadServicer):
    """支持异步配置上报流程。"""

    def __init__(self, session_manager):
        self._sm = session_manager

    async def UploadConfig(self, request, context):
        """从 session 提取 cuid 后记录配置 Payload。"""
        sid = get_metadata_dict(context).get("session", "")
        real_cuid = await self._sm.validate_session(sid)
        if not real_cuid:
            return ConfigUploadScRsp_pb2.ConfigUploadScRsp(
                Retcode=Retcode_pb2.InvalidRequest, Message="会话失效"
            )

        from app.core.tenant.context import set_search_path

        async with AsyncSessionLocal() as db:
            await set_search_path(db)
            db.add(
                ConfigUploadRecord(
                    request_guid=request.RequestGuidId,
                    client_uid=real_cuid,
                    payload=request.Payload,
                    uploaded_at=datetime.now(timezone.utc),
                )
            )
            await db.commit()
        return ConfigUploadScRsp_pb2.ConfigUploadScRsp(
            Retcode=Retcode_pb2.Success, Message="上报成功"
        )

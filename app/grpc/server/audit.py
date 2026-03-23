"""资源审计服务逻辑。

接收客户端审计事件，从 session 提取可信 cuid 防止日志伪造。
"""

import base64
from datetime import datetime, timezone

from app.models.database import AsyncSessionLocal, AuditLog
from app.grpc.api.Protobuf.Server import AuditScRsp_pb2
from app.grpc.api.Protobuf.Enum import Retcode_pb2
from app.grpc.api.Protobuf.Service import Audit_pb2_grpc
from .helpers import get_metadata_dict


class AuditServicer(Audit_pb2_grpc.AuditServicer):
    """处理异步审计日志上报。"""

    def __init__(self, session_manager):
        self._sm = session_manager

    async def LogEvent(self, request, context):
        """从 session 获取 cuid 后记录审计日志。"""
        sid = get_metadata_dict(context).get("session", "")
        real_cuid = await self._sm.validate_session(sid)
        if not real_cuid:
            return AuditScRsp_pb2.AuditScRsp(Retcode=Retcode_pb2.InvalidRequest)

        from app.core.tenant.context import set_search_path

        async with AsyncSessionLocal() as db:
            await set_search_path(db)
            db.add(
                AuditLog(
                    client_uid=real_cuid,
                    event=int(request.Event),
                    payload=base64.b64encode(request.Payload).decode("ascii"),
                    timestamp_utc=request.TimestampUtc,
                    received_at=datetime.now(timezone.utc),
                )
            )
            await db.commit()
        return AuditScRsp_pb2.AuditScRsp(Retcode=Retcode_pb2.Success)

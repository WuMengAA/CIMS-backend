"""资源审计服务逻辑。

接收并记录来自客户端的审计事件，包括配置变更、应用崩溃等关键日志。
"""

import base64
from datetime import datetime, timezone
from app.models.database import AsyncSessionLocal, AuditLog
from app.grpc.api.Protobuf.Server import AuditScRsp_pb2
from app.grpc.api.Protobuf.Enum import Retcode_pb2
from app.grpc.api.Protobuf.Service import Audit_pb2_grpc
from .helpers import get_metadata_dict, get_tenant_id_safe


class AuditServicer(Audit_pb2_grpc.AuditServicer):
    """处理 Cyrene_MSP 异步审计日志上报。"""

    def __init__(self, session_manager):
        self._sm = session_manager

    async def LogEvent(self, request, context):
        """解析审计包并将 Base64 负载存入数据库。"""
        sid = get_metadata_dict(context).get("session", "")
        tid = await self._sm.get_session_tenant(sid) or get_tenant_id_safe()

        if not await self._sm.validate_session(sid):
            return AuditScRsp_pb2.AuditScRsp(Retcode=Retcode_pb2.InvalidRequest)

        async with AsyncSessionLocal() as db:
            db.add(
                AuditLog(
                    tenant_id=tid,
                    client_uid=get_metadata_dict(context).get("cuid", ""),
                    event=int(request.Event),
                    payload=base64.b64encode(request.Payload).decode("ascii"),
                    timestamp_utc=request.TimestampUtc,
                    received_at=datetime.now(timezone.utc),
                )
            )
            await db.commit()

        return AuditScRsp_pb2.AuditScRsp(Retcode=Retcode_pb2.Success)

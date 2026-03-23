"""客户端注销服务逻辑。

处理终端设备注销请求，需验证 session 一致性。
"""

import grpc

from app.models.database import AsyncSessionLocal, ClientRecord
from app.grpc.api.Protobuf.Server import ClientRegisterScRsp_pb2
from app.grpc.api.Protobuf.Enum import Retcode_pb2
from .helpers import get_metadata_dict, get_tenant_id_safe


async def handle_unregister(sm, request, context):
    """验证 session 后注销设备记录。

    Args:
        sm: SessionManager 实例。
        request: gRPC 请求。
        context: gRPC 上下文。
    """
    sid = get_metadata_dict(context).get("session", "")
    real_cuid = await sm.validate_session(sid)

    if not real_cuid or real_cuid != request.ClientUid:
        await context.abort(grpc.StatusCode.UNAUTHENTICATED, "鉴权失败")
        return ClientRegisterScRsp_pb2.ClientRegisterScRsp()  # pragma: no cover

    tid = await sm.get_session_tenant(sid) or get_tenant_id_safe()
    from app.core.tenant.context import set_search_path

    async with AsyncSessionLocal() as db:
        await set_search_path(db)
        rec = await db.get(ClientRecord, real_cuid)
        if rec:
            await db.delete(rec)
            await db.commit()
    await sm.set_client_offline(tid, real_cuid)
    return ClientRegisterScRsp_pb2.ClientRegisterScRsp(Retcode=Retcode_pb2.Success)

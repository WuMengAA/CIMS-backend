"""实时通知下发服务。

支持向客户端发送带图标、TTS 语音以及紧急属性的即时通知弹窗。
"""

from fastapi import APIRouter, Request, Body
from app.core.tenant.context import get_tenant_id
from app.api.schemas.base import StatusResponse
from app.api.schemas.notification import NotificationPayload
from app.grpc.api.Protobuf.Server import ClientCommandDeliverScRsp_pb2
from app.grpc.api.Protobuf.Command import SendNotification_pb2
from app.grpc.api.Protobuf.Enum import Retcode_pb2, CommandTypes_pb2

router = APIRouter()


@router.post("/client/{uid}/send_notification", response_model=StatusResponse)
async def push_notify(
    uid: str, request: Request, payload: NotificationPayload = Body(...)
):
    """下发格式化的桌面通知。"""
    servicer = getattr(request.app.state, "command_servicer", None)
    if not servicer:
        return StatusResponse(status="error", message="gRPC 通道未开启")

    # 构建 Protobuf 结构
    notify = SendNotification_pb2.SendNotification(**payload.model_dump())

    cmd = ClientCommandDeliverScRsp_pb2.ClientCommandDeliverScRsp(
        RetCode=Retcode_pb2.Success,
        Type=CommandTypes_pb2.SendNotification,
        Payload=notify.SerializeToString(),
    )

    await servicer.send_command(get_tenant_id(), uid, cmd)
    return StatusResponse(status="success", message="通知已递送")

#! -*- coding:utf-8 -*-


# region Presets
# region 导入项目内建库
import Datas
import logger
import QuickValues
from Datas import get_session
from database.models import Tenant

# endregion


# region 导入辅助库
import grpc.aio
import json
from concurrent.futures import ThreadPoolExecutor

from fastapi import HTTPException

# endregion


# region 导入 Protobuf 构建文件
from Protobuf.Client import (
    ClientRegisterCsReq_pb2,
)
from Protobuf.Enum import (
    CommandTypes_pb2,
    Retcode_pb2,
)
from Protobuf.Server import (
    ClientCommandDeliverScRsp_pb2,
    ClientRegisterScRsp_pb2,
)
from Protobuf.Service import (
    ClientCommandDeliver_pb2_grpc,
    ClientRegister_pb2_grpc,
)


# endregion


# region 导入配置文件
class _Settings:
    def __init__(self):
        self.conf_name: str = "settings.json"
        self.conf_dict: dict = json.load(open(self.conf_name))

    async def refresh(self) -> dict:
        self.conf_dict = json.load(open(self.conf_name))
        return self.conf_dict


Settings = _Settings()
# endregion


# region 内建辅助函数和辅助参量
log = logger.Logger()

def _get_tenant_id_from_context(context: grpc.aio.ServicerContext) -> int:
    metadata = context.invocation_metadata()
    hostname = ""
    for m in metadata:
        if m.key == 'host':
            hostname = m.value
            break

    tenant_name = hostname.split(".")[0]
    session = get_session()
    tenant = session.query(Tenant).filter_by(name=tenant_name).first()
    session.close()
    if not tenant:
        context.abort(grpc.StatusCode.NOT_FOUND, "Tenant not found")
    return tenant.id
# endregion
# endregion


# region Main
# region 命令传递通道服务
class ClientCommandDeliverServicer(
    ClientCommandDeliver_pb2_grpc.ClientCommandDeliverServicer
):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ClientCommandDeliverServicer, cls).__new__(
                cls, *args, **kwargs
            )
            cls._instance.clients = {}
            cls._instance.executor = ThreadPoolExecutor(max_workers=10)
        return cls._instance

    async def ListenCommand(self, request_iterator, context: grpc.aio.ServicerContext):
        tenant_id = _get_tenant_id_from_context(context)
        metadata = context.invocation_metadata()
        client_uid = ""  # Initialize client_uid
        for m in metadata:  # Iterate through the metadata list
            if m.key == "cuid":
                client_uid = m.value
                break  # find it then break.

        if not client_uid:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT, "Client UID is required."
            )
            return
        log.log(
            "Client {client_uid} connected.".format(client_uid=client_uid),
            QuickValues.Log.info,
        )
        self.clients[client_uid] = context
        Datas.ClientStatus.update(client_uid, tenant_id)

        try:
            async for request in request_iterator:
                if request.Type == CommandTypes_pb2.Ping:
                    Datas.ClientStatus.update(client_uid, tenant_id)
                    log.log(
                        "Receive ping from {client_uid}".format(client_uid=client_uid),
                        QuickValues.Log.info,
                    )
                    await context.write(
                        ClientCommandDeliverScRsp_pb2.ClientCommandDeliverScRsp(
                            RetCode=Retcode_pb2.Success, Type=CommandTypes_pb2.Pong
                        )
                    )
                else:
                    log.log(
                        "Unexpected request {request} received from {client_uid}".format(
                            request=request, client_uid=client_uid
                        )
                    )
        except Exception as e:
            log.log(
                "Client {client_uid} disconnected: {e}".format(
                    client_uid=client_uid, e=e
                ),
                QuickValues.Log.info,
            )
        finally:
            self.clients.pop(client_uid, None)
            Datas.ClientStatus.offline(client_uid, tenant_id)


# endregion


# region 命令推送器
async def command(
    client_uid: str, command_type: CommandTypes_pb2.CommandTypes, payload: bytes = b""
):
    servicer = ClientCommandDeliverServicer()
    if client_uid not in servicer.clients:
        log.log(
            "Send {command} to {client_uid}, failed.".format(
                command=command_type, client_uid=client_uid
            ),
            QuickValues.Log.error,
        )
        raise HTTPException(
            status_code=404, detail=f"Client not found or not connected: {client_uid}"
        )
    log.log(
        "Send {command} to {client_uid}".format(
            command=command_type, client_uid=client_uid
        ),
        QuickValues.Log.info,
    )
    await servicer.clients[client_uid].write(
        ClientCommandDeliverScRsp_pb2.ClientCommandDeliverScRsp(
            RetCode=Retcode_pb2.Success, Type=command_type, Payload=payload
        )
    )


# endregion


# region 注册服务
class ClientRegisterServicer(ClientRegister_pb2_grpc.ClientRegisterServicer):
    async def Register(
        self,
        request: ClientRegisterCsReq_pb2.ClientRegisterCsReq,
        context: grpc.aio.ServicerContext,
    ) -> ClientRegisterScRsp_pb2.ClientRegisterScRsp:
        tenant_id = _get_tenant_id_from_context(context)
        clients = Datas.Clients.refresh(tenant_id)
        client_uid = request.clientUid
        client_id = request.clientId
        if client_uid in clients:
            log.log(
                "Client {client_uid} registered as {client_id}, but register again.".format(
                    client_uid=client_uid, client_id=client_id
                ),
                QuickValues.Log.warning,
            )
            Datas.Clients.register(client_uid, client_id, tenant_id)
            return ClientRegisterScRsp_pb2.ClientRegisterScRsp(
                Retcode=Retcode_pb2.Registered,
                Message=f"Client already registered: {client_uid}",
            )
        else:
            log.log(
                "Client {client_uid} registered as {client_id}".format(
                    client_uid=client_uid, client_id=client_id
                ),
                QuickValues.Log.info,
            )
            Datas.Clients.register(client_uid, client_id, tenant_id)
            return ClientRegisterScRsp_pb2.ClientRegisterScRsp(
                Retcode=Retcode_pb2.Success, Message=f"Client registered: {client_uid}"
            )

    async def UnRegister(self, request, context):
        return ClientRegisterScRsp_pb2.ClientRegisterScRsp(
            Retcode=Retcode_pb2.ServerInternalError, Message="Not implemented"
        )


# endregion


# region 启动函数
async def start(port=50051):
    server = grpc.aio.server()
    ClientRegister_pb2_grpc.add_ClientRegisterServicer_to_server(
        ClientRegisterServicer(), server
    )
    ClientCommandDeliver_pb2_grpc.add_ClientCommandDeliverServicer_to_server(
        ClientCommandDeliverServicer(), server
    )
    server.add_insecure_port("0.0.0.0:{port}".format(port=port))
    log.log(
        "Starting gRPC server on {listen_addr}".format(
            listen_addr="0.0.0.0:{port}".format(port=port)
        ),
        QuickValues.Log.info,
    )
    await server.start()
    await server.wait_for_termination()


# endregion
# endregion


# region Running Directly processor
if __name__ == "__main__":
    log.log(message="Directly started, refused.", status=QuickValues.Log.error)
# endregion

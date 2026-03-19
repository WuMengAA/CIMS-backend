"""命令分发双向流。

维护客户端长连接，并提供异步队列机制，将管理指令推送到远程终端。
"""

import asyncio
import logging
from typing import Dict
from app.grpc.api.Protobuf.Service import ClientCommandDeliver_pb2_grpc
from .helpers import get_metadata_dict, get_tenant_id_safe

logger = logging.getLogger(__name__)


class ClientCommandDeliverServicer(
    ClientCommandDeliver_pb2_grpc.ClientCommandDeliverServicer
):
    """处理 Cyrene_MSP 指令监听与心跳。"""

    def __init__(self, session_manager):
        self._sm = session_manager
        self.client_queues: Dict[str, asyncio.Queue] = {}

    async def ListenCommand(self, request_iterator, context):
        """双向流监听器：建立连接、维持心跳、下发异步指令。"""
        md = get_metadata_dict(context)
        cuid, sid = md.get("cuid"), md.get("session", "")
        tid = await self._sm.get_session_tenant(sid) or get_tenant_id_safe()

        # 注册在线状态与消息队列
        await self._sm.set_client_online(tid, cuid, ip=context.peer() or "")
        q_key, queue = f"{tid}:{cuid}", asyncio.Queue()
        self.client_queues[q_key] = queue

        try:
            # 内部循环：处理从客户端发来的心跳 (Ping) 和响应
            # 为节省行数，主要分流到 command_utils.py 中
            from .command_utils import run_command_loop

            async for resp in run_command_loop(
                self, request_iterator, queue, tid, cuid
            ):
                yield resp
        finally:
            self.client_queues.pop(q_key, None)
            await self._sm.set_client_offline(tid, cuid)

    async def send_command(self, tid, cuid, cmd):
        """API 向特定客户端注入指令的公共方法。"""
        key = f"{tid}:{cuid}"
        if key in self.client_queues:
            await self.client_queues[key].put(cmd)

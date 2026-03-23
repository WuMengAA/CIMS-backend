"""命令流辅助工具。

封装双向流异步读写循环，含心跳响应、Ping 速率限制与空闲超时。
"""

import asyncio
import time
from app.grpc.api.Protobuf.Enum import Retcode_pb2, CommandTypes_pb2
from app.grpc.api.Protobuf.Server import ClientCommandDeliverScRsp_pb2
from .stream_timeout import get_with_timeout

# Ping 最小间隔（秒），防止客户端洪泛
_MIN_PING_INTERVAL = 1.0


async def run_command_loop(servicer, request_iterator, queue, tid, cuid):
    """运行长连接读写工作流，含速率限制和空闲超时。"""
    last_ping = 0.0

    async def read_task():
        nonlocal last_ping
        async for req in request_iterator:
            if req.Type == CommandTypes_pb2.Ping:
                now = time.monotonic()
                if now - last_ping < _MIN_PING_INTERVAL:
                    continue  # 速率限制：丢弃过频心跳
                last_ping = now
                await servicer._sm.update_heartbeat(tid, cuid)
                pong = ClientCommandDeliverScRsp_pb2.ClientCommandDeliverScRsp(
                    RetCode=Retcode_pb2.Success, Type=CommandTypes_pb2.Pong
                )
                await queue.put(pong)

    task = asyncio.create_task(read_task())
    try:
        while True:
            # 使用带超时的读取，防止 TCP 半开连接永久阻塞
            msg = await get_with_timeout(queue)
            yield msg
            queue.task_done()
    except (asyncio.CancelledError, asyncio.TimeoutError):
        task.cancel()

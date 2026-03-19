"""命令流辅助工具。

封装用于处理客户端双向流监听中的异步读写循环，实现心跳自动响应与队列分发。
"""

from app.grpc.api.Protobuf.Enum import Retcode_pb2, CommandTypes_pb2
from app.grpc.api.Protobuf.Server import ClientCommandDeliverScRsp_pb2


async def run_command_loop(servicer, request_iterator, queue, tid, cuid):
    """运行长连接读写工作流。"""

    # 异步读取客户端消息的任务
    async def read_task():
        async for req in request_iterator:
            if req.Type == CommandTypes_pb2.Ping:
                await servicer._sm.update_heartbeat(tid, cuid)
                await queue.put(
                    ClientCommandDeliverScRsp_pb2.ClientCommandDeliverScRsp(
                        RetCode=Retcode_pb2.Success, Type=CommandTypes_pb2.Pong
                    )
                )

    import asyncio

    task = asyncio.create_task(read_task())

    try:
        while True:
            # 持续从下发队列中提取指令并返回给 yield (通过 ListenCommand)
            msg = await queue.get()
            yield msg
            queue.task_done()
    except asyncio.CancelledError:
        task.cancel()

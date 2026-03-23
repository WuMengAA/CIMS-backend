"""gRPC 流空闲超时工具。

封装带超时的队列读取，防止 TCP 半开连接导致的资源泄漏。
"""

import asyncio
from typing import Any

# 流空闲超时（秒）：客户端若在此时间内无心跳则断开
STREAM_IDLE_TIMEOUT = 120


async def get_with_timeout(
    queue: asyncio.Queue, timeout: float = STREAM_IDLE_TIMEOUT
) -> Any:
    """从队列中读取一条消息，超时则抛出 TimeoutError。

    Args:
        queue: 异步消息队列。
        timeout: 最大等待秒数。

    Raises:
        asyncio.TimeoutError: 超过空闲时间限制。
    """
    return await asyncio.wait_for(queue.get(), timeout=timeout)

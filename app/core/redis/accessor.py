"""提供对全局 Redis 连接池的统一访问。

确保所有业务逻辑在调用 Redis 前连接池均已就绪。
"""

import redis.asyncio as aioredis
from .pool import _pool


def get_redis() -> aioredis.Redis:
    """Access the currently active Redis connection pool.

    Returns:
        The active aioredis.Redis pool singleton.

    Raises:
        RuntimeError: If the pool has not been initialized via init_redis().
    """
    if _pool is None:
        raise RuntimeError("Redis pool not initialised — call init_redis() first")
    return _pool

"""提供对指定 Redis 逻辑 DB 连接池的统一访问。

确保所有业务逻辑在调用 Redis 前连接池均已就绪。
"""

import redis.asyncio as aioredis
from .pool import get_pool


def get_redis(db: int = 0) -> aioredis.Redis:
    """获取指定逻辑 DB 的 Redis 连接池。

    Args:
        db: Redis 逻辑数据库编号（0-15）。

    Raises:
        RuntimeError: 若该 DB 的连接池尚未初始化。
    """
    pool = get_pool(db)
    if pool is None:
        raise RuntimeError(f"Redis DB {db} 未初始化 — 请先调用 init_redis()")
    return pool

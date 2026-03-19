"""Redis 连接池生命周期管理。

负责异步 Redis 客户端的初始化、连接池配置以及在应用关闭时优雅地释放资源。
"""

import logging
from typing import Optional
import redis.asyncio as aioredis
from app.core.config import REDIS_URL

logger = logging.getLogger(__name__)

# Global reference for the connection pool
_pool: Optional[aioredis.Redis] = None


async def init_redis() -> aioredis.Redis:
    """初始化全局 Redis 连接池并验证连通性。"""
    global _pool
    if _pool is not None:
        try:
            await _pool.ping()
            return _pool
        except Exception:
            try:
                await _pool.aclose()
            except Exception:
                pass
            _pool = None

    _pool = aioredis.from_url(
        REDIS_URL,
        decode_responses=True,
        max_connections=20,
    )
    await _pool.ping()
    logger.info("Redis connected: %s", REDIS_URL.split("@")[-1])
    return _pool


async def close_redis() -> None:
    """安全关闭 Redis 客户端，确保所有挂起的命令执行完成。"""
    global _pool
    if _pool is not None:
        await _pool.aclose()
        _pool = None
        logger.info("Redis connection closed")

"""Redis 多逻辑 DB 连接池管理。

按功能分配独立的 Redis Logical DB，实现键空间物理隔离。
"""

import sys
import logging
from typing import Optional
import redis.asyncio as aioredis
from app.core.config import REDIS_URL

logger = logging.getLogger(__name__)
_pools: dict[int, aioredis.Redis] = {}


def _build_url(db: int) -> str:
    """将基础 URL 的 DB 编号替换为指定值。"""
    return f"{REDIS_URL.rsplit('/', 1)[0]}/{db}"


async def init_redis(*, dbs: tuple[int, ...] = (0, 1, 2)) -> None:
    """为每个指定的逻辑 DB 初始化独立连接池。"""
    for db in dbs:
        if db in _pools:
            try:
                await _pools[db].ping()
                continue
            except Exception:
                try:
                    await _pools[db].aclose()
                except Exception:
                    pass
        pool = aioredis.from_url(
            _build_url(db), decode_responses=True, max_connections=20
        )
        await pool.ping()
        _pools[db] = pool
    pkg = sys.modules.get("app.core.redis")
    if pkg and "_pool" in pkg.__dict__:
        pkg.__dict__["_pool"] = _pools.get(0)
    logger.info("Redis 已连接 DB: %s", list(_pools.keys()))


def get_pool(db: int = 0) -> Optional[aioredis.Redis]:
    """获取指定 DB 的连接池引用。"""
    return _pools.get(db)


async def close_redis() -> None:
    """关闭所有 DB 的连接池。"""
    for db in list(_pools.keys()):
        await _pools[db].aclose()
    _pools.clear()
    logger.info("Redis 全部连接已关闭")

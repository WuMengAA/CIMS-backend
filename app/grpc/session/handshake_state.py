"""握手状态持久化。

记录处于中间状态（待确认）的挑战令牌，并应用 TTL 过期机制防止堆积。
"""

from app.core.redis.accessor import get_redis

HANDSHAKE_TTL = 120


async def store_handshake_challenge(tenant_id: str, cuid: str, token: str):
    """在 Redis 中暂存解密后的令牌 120 秒，等待客户端 CompleteHandshake。"""
    rd = get_redis()
    key = f"handshake:{tenant_id}:{cuid}"
    await rd.set(key, token, ex=HANDSHAKE_TTL)


async def pop_handshake_challenge(tenant_id: str, cuid: str) -> str:
    """提取并销毁待确认的令牌。"""
    rd, key = get_redis(), f"handshake:{tenant_id}:{cuid}"
    val = await rd.get(key)
    if val:
        await rd.delete(key)
    return val

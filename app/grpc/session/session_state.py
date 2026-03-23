"""活跃会话（Session）状态。

建立 Session ID 与 租户/客户端 的多重映射，支撑多路复用下的身份鉴权。
"""

import uuid
from app.core.config import REDIS_DB_SESSION
from app.core.redis.accessor import get_redis

SESSION_TTL = 86400  # 24小时有效


async def create_new_session(tenant_id: str, cuid: str) -> str:
    """生成全局唯一的 Session ID 并绑定元信息到 Redis。"""
    rd = get_redis(REDIS_DB_SESSION)
    sid = str(uuid.uuid4())
    key = f"session:{sid}"
    await rd.hset(key, mapping={"cuid": cuid, "tenant_id": tenant_id})
    await rd.expire(key, SESSION_TTL)
    return sid


async def get_session_info(session_id: str) -> dict:
    """根据 ID 检索会话元数据（租户 ID 和客户端 UID）。"""
    if not session_id:
        return {}
    rd = get_redis(REDIS_DB_SESSION)
    return await rd.hgetall(f"session:{session_id}")

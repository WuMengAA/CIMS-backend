"""管理端令牌注销与软撤销。

提供令牌宽限期软删除功能，防止并发刷新时的竞争条件。
"""

from app.core.config import REDIS_DB_AUTH
from app.core.redis.accessor import get_redis

# 宽限期：旧令牌在撤销后仍保持只读有效的秒数
_GRACE_TTL = 30


async def revoke_token(token: str, *, tenant_id: str = "") -> bool:
    """软撤销令牌：标记为已刷新并保留短暂宽限期。

    Returns:
        若令牌存在并被成功标记则返回 True。
    """
    if not token:
        return False

    rd = get_redis(REDIS_DB_AUTH)
    key = _build_key(tenant_id, token)
    exists = await rd.exists(key)
    if not exists:
        return False

    # 标记为已刷新，保留宽限期后自动过期
    await rd.hset(key, "refreshed", "1")
    await rd.expire(key, _GRACE_TTL)
    return True


def _build_key(tenant_id: str, token: str) -> str:
    """构建租户隔离的 Redis 键。"""
    return f"auth:{tenant_id}:{token}" if tenant_id else f"auth::{token}"

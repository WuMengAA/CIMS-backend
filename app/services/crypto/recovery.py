"""2FA 恢复码生成与验证。

生成 8 个一次性恢复码，使用后消耗。
恢复码存储在 Redis 中，绑定用户 ID。
"""

import secrets

from app.core.config import REDIS_DB_AUTH
from app.core.redis.accessor import get_redis

# 恢复码数量和长度
_CODE_COUNT = 8
_CODE_LENGTH = 8
_KEY_PREFIX = "recovery_codes"


def generate_recovery_codes() -> list[str]:
    """生成 8 个一次性恢复码。"""
    return [secrets.token_hex(_CODE_LENGTH // 2).upper() for _ in range(_CODE_COUNT)]


async def store_recovery_codes(user_id: str, codes: list[str]) -> None:
    """将恢复码存入 Redis（覆盖旧码）。"""
    rd = get_redis(REDIS_DB_AUTH)
    key = f"{_KEY_PREFIX}:{user_id}"
    await rd.delete(key)
    if codes:
        await rd.sadd(key, *codes)


async def use_recovery_code(user_id: str, code: str) -> bool:
    """验证并消耗一个恢复码。

    Returns:
        True 表示恢复码有效并已消耗。
    """
    rd = get_redis(REDIS_DB_AUTH)
    key = f"{_KEY_PREFIX}:{user_id}"
    removed = await rd.srem(key, code.upper())
    return removed > 0


async def get_remaining_count(user_id: str) -> int:
    """查询剩余恢复码数量。"""
    rd = get_redis(REDIS_DB_AUTH)
    return await rd.scard(f"{_KEY_PREFIX}:{user_id}")

"""Argon2id 密码哈希与验证。

采用 OWASP 推荐的 Argon2id 算法，
参数：time_cost=3, memory_cost=65536(64MB), parallelism=4。
"""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Argon2id 参数配置（符合 OWASP 最新推荐）
_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
)


def hash_password(plain: str) -> str:
    """将明文密码哈希为 Argon2id 摘要字符串。"""
    return _hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """时间常量比对验证密码，防止计时攻击。

    Returns:
        True 表示密码匹配，False 表示不匹配。
    """
    try:
        return _hasher.verify(hashed, plain)
    except VerifyMismatchError:
        return False

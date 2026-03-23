"""Redis 核心工具模块导出。

整合 Redis 管理和访问器函数，提供便捷的统一导入。
"""

from .pool import init_redis, close_redis  # noqa: F401
from .accessor import get_redis  # noqa: F401

__all__ = ["init_redis", "close_redis", "get_redis"]

# 兼容测试：暴露 _pool 供 redis_mod._pool = None 覆盖使用
_pool = None

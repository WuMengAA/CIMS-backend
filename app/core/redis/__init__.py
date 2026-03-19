"""Redis core utility module exports.

Consolidates Redis management and accessor functions for easy imports.
"""

from .pool import init_redis, close_redis
from .accessor import get_redis

__all__ = ["init_redis", "close_redis", "get_redis"]

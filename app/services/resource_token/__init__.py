"""资源令牌服务入口。"""

from .creator import create_token
from .resolver import resolve_token

__all__ = ["create_token", "resolve_token"]

"""认证服务入口。

简化令牌生命周期管理的统一导入接口。
"""

from .generator import generate_token
from .validator import validate_and_refresh
from .revoker import revoke_token

__all__ = ["generate_token", "validate_and_refresh", "revoke_token"]

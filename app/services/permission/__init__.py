"""权限服务入口。

提供权限检查和授予/撤销的统一访问接口。
"""

from .checker import check_permission
from .grants import grant_permission, revoke_permission

__all__ = [
    "check_permission",
    "grant_permission",
    "revoke_permission",
]

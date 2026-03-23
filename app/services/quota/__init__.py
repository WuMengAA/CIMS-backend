"""限额服务入口。

提供限额检查/扣减和管理配置的统一访问接口。
"""

from .enforcer import check_quota, increment_quota
from .manager import set_quota, get_quotas

__all__ = [
    "check_quota",
    "increment_quota",
    "set_quota",
    "get_quotas",
]

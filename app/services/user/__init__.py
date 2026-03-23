"""用户服务入口。

提供注册、登录、管理和角色操作的统一访问接口。
"""

from .register import register_user
from .login import login_user

__all__ = ["register_user", "login_user"]

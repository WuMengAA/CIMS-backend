"""管理端 API 聚合路由。

将所有管理子模块注册到管理应用的单一顶层路由中。
"""

from fastapi import APIRouter

from .auth_routes import router as auth_router
from .user_routes import router as user_router
from .role_routes import router as role_router
from .account_routes import router as account_router
from .quota_routes import router as quota_router
from .permission_routes import router as perm_router
from .totp_routes import router as totp_router

# 导入以触发路由注册副作用
from . import totp_enable, totp_confirm, totp_verify  # noqa: F401

router = APIRouter()

# 认证子路由
router.include_router(auth_router, prefix="/auth")
# 用户管理子路由
router.include_router(user_router, prefix="/users")
# 角色分级子路由
router.include_router(role_router, prefix="/roles")
# 账户管理子路由
router.include_router(account_router, prefix="/accounts")
# 限额管理子路由
router.include_router(quota_router, prefix="/quotas")
# 权限管理子路由
router.include_router(perm_router, prefix="/permissions")
# 2FA 路由（前缀已内含 /admin/auth/2fa）
router.include_router(totp_router)

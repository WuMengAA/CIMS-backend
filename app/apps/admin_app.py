"""管理控制台 API 应用定义。

仅挂载管理员权限相关的认证与多租户管理端点。
"""

from fastapi import FastAPI
from app.api.admin.router import router as admin_router
from app.api.command.router import router as command_router
from app.core.auth.http_middleware import TenantMiddleware
from app.core.auth.admin_middleware import AdminAuthMiddleware

admin_app = FastAPI(title="CIMS 管理 API", version="0.2.0", redirect_slashes=False)

# 全局租户隔离中间件
admin_app.add_middleware(TenantMiddleware)

# 管理端令牌认证中间件
admin_app.add_middleware(AdminAuthMiddleware)

# 管理路由与指令下发路由
admin_app.include_router(admin_router, prefix="/admin", tags=["Admin"])
admin_app.include_router(command_router, prefix="/command", tags=["Command"])


@admin_app.get("/")
async def root():  # pragma: no cover
    """管理端 API 状态检测。"""
    return {"message": "CIMS 管理端运行中"}

"""管理控制台 API 应用定义。

仅挂载管理员权限相关的认证与多租户管理端点。
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.admin.router import router as admin_router
from app.api.command.router import router as command_router
from app.core.auth.http_middleware import TenantMiddleware
from app.core.auth.admin_middleware import AdminAuthMiddleware

logger = logging.getLogger(__name__)

admin_app = FastAPI(title="CIMS 管理 API", version="0.2.0", redirect_slashes=False)

# 全局租户隔离中间件
admin_app.add_middleware(TenantMiddleware)

# 管理端令牌认证中间件
admin_app.add_middleware(AdminAuthMiddleware)

# 管理路由与指令下发路由
admin_app.include_router(admin_router, prefix="/admin", tags=["Admin"])
admin_app.include_router(command_router, prefix="/command", tags=["Command"])


@admin_app.exception_handler(Exception)
async def _global_exc(request: Request, exc: Exception):
    """全局异常拦截，避免泄露内部信息。"""
    logger.exception("未处理异常: %s %s", request.url.path, exc)
    return JSONResponse(
        status_code=500, content={"detail": "服务器内部错误"}
    )


@admin_app.get("/")
async def root():  # pragma: no cover
    """管理端 API 状态检测。"""
    return {"message": "CIMS 管理端运行中"}

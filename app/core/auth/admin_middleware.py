"""管理端令牌认证中间件。

通过 Redis 会话令牌验证用户身份，
将已认证的 user_id 注入 request.state。
兼容旧版 command 域令牌以保持 /command/* 路由可用。
"""

import logging

logger = logging.getLogger(__name__)

from fastapi import Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import JSONResponse

from app.core.config import REDIS_DB_AUTH
from app.core.redis.accessor import get_redis
from app.core.tenant.context import get_tenant_id

# 免认证路径白名单
_EXEMPT = {"/", "/admin/auth/login", "/admin/auth/register"}
_DENY = JSONResponse(status_code=403, content={"detail": "权限不足"})
_NO_AUTH = JSONResponse(status_code=401, content={"detail": "未认证"})


class AdminAuthMiddleware(BaseHTTPMiddleware):
    """管理端会话令牌认证拦截器。"""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """验证 Bearer Token 并注入用户身份。"""
        path = request.url.path
        if path in _EXEMPT:
            return await call_next(request)
        if not path.startswith(("/admin", "/command")):
            return await call_next(request)
        # 提取 Bearer Token
        auth = request.headers.get("authorization", "")
        if not auth.startswith("Bearer "):
            return _NO_AUTH
        token = auth[7:]
        # 尝试新式会话令牌
        from app.core.auth.dependencies import (
            resolve_user_from_token,
        )

        user_id = await resolve_user_from_token(token)
        if user_id:
            request.state.current_user_id = user_id
            return await call_next(request)
        # 回退：旧式 command 域令牌
        if path.startswith("/command"):
            ok = await _check_legacy_token(token)
            if ok:
                return await call_next(request)
        client_ip = request.client.host if request.client else "unknown"
        logger.warning(
            "认证失败：ip=%s path=%s", client_ip, path
        )
        return _DENY


async def _check_legacy_token(token: str) -> bool:
    """检查旧式 auth:{tenant_id}:{token} 格式的令牌。"""
    rd = get_redis(REDIS_DB_AUTH)
    tid = get_tenant_id()
    if not tid:
        return False
    key = f"auth:{tid}:{token}"
    data = await rd.hgetall(key)
    return bool(data and data.get("scope") == "command")

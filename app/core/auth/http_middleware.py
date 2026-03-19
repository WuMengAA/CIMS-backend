"""HTTP 多租户路由中间件。

拦截请求、解析主机名，并确保在处理器执行前已加载正确的租户上下文。
"""

from fastapi import Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from app.core.tenant.host_parser import extract_slug_from_host
from starlette.responses import JSONResponse
from .session import run_in_tenant_context


class TenantMiddleware(BaseHTTPMiddleware):
    """路由器级别的二级域名拦截处理。"""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """带域名解析的路由拦截逻辑。"""
        path = request.url.path

        if path in ["/", "/admin/auth/login"]:
            return await call_next(request)

        slug = extract_slug_from_host(request.headers.get("host", ""))
        if not slug:
            return JSONResponse(
                status_code=404,
                content={"detail": "Tenant ID missing in host"},
            )

        return await run_in_tenant_context(slug, call_next, request)

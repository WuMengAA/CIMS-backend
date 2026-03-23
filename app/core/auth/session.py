"""HTTP 请求的租户上下文包装器。

封装了在异步请求-响应生命周期内设置和重置
租户 ContextVar 的逻辑。
"""

from typing import Any, Callable

from starlette.responses import JSONResponse

from app.core.tenant.context import tenant_ctx
from app.core.tenant.resolver import resolve_account
from app.models.engine import AsyncSessionLocal


async def run_in_tenant_context(slug: str, call_next: Callable, request: Any) -> Any:
    """解析账户并在隔离的上下文中执行下一个处理器。"""
    async with AsyncSessionLocal() as db:
        account = await resolve_account(slug, db)
    if not account:
        return JSONResponse(
            status_code=404,
            content={"detail": "账户不存在或已停用"},
        )
    token = tenant_ctx.set(account.id)
    try:
        request.state.tenant_id = account.id
        return await call_next(request)
    finally:
        tenant_ctx.reset(token)

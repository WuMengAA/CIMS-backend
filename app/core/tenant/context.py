"""多租户执行上下文管理。

使用 ContextVar 在异步调用链中传递 tenant_id，确保同一请求内的
租户数据隔离。
"""

from contextvars import ContextVar

# Per-request tenant ID (set by middleware/interceptor)
tenant_ctx: ContextVar[str] = ContextVar("tenant_id")


def get_tenant_id() -> str:
    """保存当前请求范围内的活跃租户 ID。

    Returns:
        The stored tenant_id as a string.

    Raises:
        RuntimeError: If no tenant context has been set for this request.
    """
    try:
        return tenant_ctx.get()
    except LookupError:
        raise RuntimeError("No tenant context set for this request")

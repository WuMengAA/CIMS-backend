"""多租户执行上下文管理。

使用 ContextVar 在异步调用链中传递 tenant_id 和 schema，
确保同一请求内的租户数据隔离。
"""

import re
from contextvars import ContextVar
from sqlalchemy import text

# 每请求的租户 ID（由中间件/拦截器设置）
tenant_ctx: ContextVar[str] = ContextVar("tenant_id")

# 每请求的数据库 Schema 名（由中间件设置）
schema_ctx: ContextVar[str] = ContextVar("schema", default="public")

_SAFE_ID = re.compile(r"^[a-z0-9_\-]+$")


def safe_identifier(name: str) -> str:
    """校验 SQL 标识符仅含安全字符，防止注入。"""
    if not _SAFE_ID.match(name):
        raise ValueError(f"Unsafe SQL identifier: {name!r}")
    return name


def get_tenant_id() -> str:
    """获取当前请求范围内的活跃租户 ID。

    Raises:
        RuntimeError: 若当前请求未设置租户上下文。
    """
    try:
        return tenant_ctx.get()
    except LookupError:
        raise RuntimeError("No tenant context set for this request")


def get_schema() -> str:
    """获取当前请求的目标数据库 Schema 名称。"""
    return schema_ctx.get()


async def set_search_path(session, schema: str | None = None) -> None:
    """在数据库会话上安全设置 search_path。"""
    s = safe_identifier(schema or get_schema())
    if s != "public":
        await session.execute(text(f'SET search_path TO "{s}", public'))

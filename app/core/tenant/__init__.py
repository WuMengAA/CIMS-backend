"""多租户管理核心模块。

提供请求范围内的上下文管理、基于主机名的子域名解析
和混合账户解析的统一导出。
"""

from .context import (
    tenant_ctx,
    get_tenant_id,
    schema_ctx,
    get_schema,
    safe_identifier,
    set_search_path,
)
from .host_parser import extract_slug_from_host
from .resolver import resolve_account

__all__ = [
    "tenant_ctx",
    "get_tenant_id",
    "schema_ctx",
    "get_schema",
    "safe_identifier",
    "set_search_path",
    "extract_slug_from_host",
    "resolve_account",
]

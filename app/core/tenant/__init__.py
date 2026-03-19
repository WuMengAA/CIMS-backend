"""Multi-tenant management core module.

Provides unified exports for request-scoped context, host-based
subdomain parsing, and hybrid resolution.
"""

from .context import tenant_ctx, get_tenant_id
from .host_parser import extract_slug_from_host
from .resolver import resolve_tenant

__all__ = [
    "tenant_ctx",
    "get_tenant_id",
    "extract_slug_from_host",
    "resolve_tenant",
]

"""gRPC tenant identification interceptor.

Identifies the active tenant for gRPC calls using authority headers or
explicit metadata, ensuring context-awareness in async calls.
"""

import grpc
from app.core.tenant.context import tenant_ctx
from app.core.tenant.resolver import resolve_tenant
from app.core.tenant.host_parser import extract_slug_from_host
from app.models.database import AsyncSessionLocal


class TenantInterceptor(grpc.aio.ServerInterceptor):
    """Server-side gRPC tenant resolution."""

    async def intercept_service(self, continuation, handler_call_details):
        """Extract tenant-id from metadata and apply to context."""
        metadata = dict(handler_call_details.invocation_metadata)
        authority = metadata.get(":authority", "")
        slug = extract_slug_from_host(authority) or metadata.get("tenant-id")

        if slug:
            async with AsyncSessionLocal() as db:
                tenant = await resolve_tenant(slug, db)
            if tenant:
                tenant_ctx.set(tenant.id)

        return await continuation(handler_call_details)

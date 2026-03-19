"""Client resource access redirection.

Generates IP-bound resource tokens and redirects clients
to the central GET endpoint.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from app.core.tenant.context import get_tenant_id
from app.services.resource_token.creator import create_token

router = APIRouter()

# Models mapped for validation (aggregator used in app initialization)
VALID_RESOURCES = [
    "ClassPlan",
    "TimeLayout",
    "Subjects",
    "Policy",
    "DefaultSettings",
    "Components",
    "Credentials",
]


@router.get("/v1/client/{resource_type}")
async def get_client_resource(resource_type: str, name: str, request: Request):
    """Protocol-specific redirect to the token-gated downloader."""
    if resource_type not in VALID_RESOURCES:
        raise HTTPException(status_code=400, detail="Invalid resource")

    tenant_id = get_tenant_id()
    client_ip = request.client.host if request.client else ""

    token = await create_token(tenant_id, resource_type, name, client_ip=client_ip)
    return RedirectResponse(url=f"/get?token={token}", status_code=302)

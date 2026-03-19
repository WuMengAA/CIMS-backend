"""高危租户管理操作接口。

封装了重置租户密钥、硬删除等具有破坏性或高权限的租户管理任务。
"""

import secrets
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.core.config import BASE_DOMAIN, CLIENT_PORT, GRPC_PORT
from app.core.redis.accessor import get_redis
from app.api.schemas.tenant import TenantOut
from .helpers import get_tenant_or_404, tenant_to_out

router = APIRouter()


@router.post("/{tenant_id}/rotate-key", response_model=TenantOut)
async def rotate_api_key(tenant_id: str, db: AsyncSession = Depends(get_db)):
    """Generate a new API key for the specified tenant."""
    tenant = await get_tenant_or_404(tenant_id, db)
    tenant.api_key = secrets.token_urlsafe(32)
    await db.commit()
    await get_redis().delete(f"tenant:{tenant.slug}")
    return tenant_to_out(tenant)


@router.get("/{tenant_id}/management-config")
async def tenant_management_config(
    tenant_id: str,
    class_identity: str = "",
    db: AsyncSession = Depends(get_db),
):
    """Generate ManagementServer.json for class-end join."""
    tenant = await get_tenant_or_404(tenant_id, db)
    base = f"http://{tenant.slug}.{BASE_DOMAIN}"

    return {
        "IsManagementEnabled": True,
        "ManagementServerKind": 1,
        "ManagementServer": f"{base}:{CLIENT_PORT}",
        "ManagementServerGrpc": f"{base}:{GRPC_PORT}",
        "ClassIdentity": class_identity,
    }

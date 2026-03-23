"""引导配置生成服务。

由租户子域名访问，动态下发引导客户端加入管理服务的 JSON 配置文件。
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.session import get_db
from app.core.tenant.context import get_tenant_id
from app.core.config import BASE_DOMAIN, CLIENT_PORT, GRPC_PORT

router = APIRouter()


@router.get("/v1/management-config")
async def get_config(
    class_identity: str = "",
    db: AsyncSession = Depends(get_db),
):
    """根据子域名自动计算并返回 ManagementServer.json。"""
    tenant_id = get_tenant_id()
    stmt = select(Account).where(Account.id == tenant_id)
    account = (await db.execute(stmt)).scalar_one_or_none()
    slug = account.slug if account else "unknown"
    root = f"http://{slug}.{BASE_DOMAIN}"
    return {
        "IsManagementEnabled": True,
        "ManagementServerKind": 1,
        "ManagementServer": f"{root}:{CLIENT_PORT}",
        "ManagementServerGrpc": f"{root}:{GRPC_PORT}",
        "ClassIdentity": class_identity,
        "ManifestUrlTemplate": "",
    }

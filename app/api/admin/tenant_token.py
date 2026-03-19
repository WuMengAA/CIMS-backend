"""租户维度的管理令牌接口。

允许管理员为特定租户生成用于 API 访问的长期或短期令牌。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.services import auth_token
from .helpers import get_tenant_or_404

router = APIRouter()


@router.post("/{tenant_id}/auth/token")
async def create_command_token(tenant_id: str, db: AsyncSession = Depends(get_db)):
    """Exchange admin context for a tenant-scoped command token."""
    tenant = await get_tenant_or_404(tenant_id, db)
    token = await auth_token.generate_token("command", tenant_id=tenant.id)
    return {"token": token, "expires_in": 300, "token_type": "Bearer"}

"""资源授权令牌。

为特定的配置文件生成短期访问令牌，使得客户端可以通过非鉴权接口安全下载数据。
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.core.tenant.context import get_tenant_id
from app.services.resource_token.creator import create_token
from .model_map import MODEL_MAP

router = APIRouter()


@router.get("/{resource_type}/token")
async def get_resource_token(
    resource_type: str, name: str, db: AsyncSession = Depends(get_db)
):
    """验证资源存在性并签发一个单次有效的访问令牌。"""
    tenant_id = get_tenant_id()
    model = MODEL_MAP.get(resource_type)
    if not model:
        return {"status": "error", "message": "无效类型"}

    stmt = select(model).where(model.tenant_id == tenant_id, model.name == name)
    record = (await db.execute(stmt)).scalar_one_or_none()
    if not record:
        return {"status": "error", "message": f"{name} 不存在"}

    token = await create_token(tenant_id, resource_type, name)
    return {"token": token, "url": f"/get?token={token}"}

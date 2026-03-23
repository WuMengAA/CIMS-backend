"""限额管理路由。

提供账户限额查询和设置端点，
需要超级管理员权限。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import get_db
from app.core.auth.dependencies import require_role
from app.api.schemas.quota import QuotaSetRequest, QuotaOut
from app.services.quota.manager import get_quotas, set_quota

router = APIRouter()
_superadmin = require_role(100)


@router.get("/{account_id}", response_model=list[QuotaOut])
async def list_quotas(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    _user=Depends(_superadmin),
):
    """查询账户的所有限额（需超级管理员）。"""
    quotas = await get_quotas(account_id, db)
    return [_to_out(q) for q in quotas]


@router.put("/{account_id}", response_model=QuotaOut)
async def update_quota(
    account_id: str,
    body: QuotaSetRequest,
    db: AsyncSession = Depends(get_db),
    _user=Depends(_superadmin),
):
    """设置或更新账户限额（需超级管理员）。"""
    quota = await set_quota(account_id, body.quota_key, body.max_value, db)
    return _to_out(quota)


def _to_out(q) -> QuotaOut:
    """将 AccountQuota 模型转换为响应模型。"""
    return QuotaOut(
        id=q.id,
        account_id=q.account_id,
        quota_key=q.quota_key,
        max_value=q.max_value,
        current_value=q.current_value,
    )

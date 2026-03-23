"""账户管理路由。

提供账户列表查询和详情查看端点，
需要管理员或以上权限。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import get_db
from app.models.account import Account
from app.core.auth.dependencies import require_role
from app.api.schemas.account import AccountOut

router = APIRouter()
_admin = require_role(90)


@router.get("", response_model=list[AccountOut])
async def list_accounts(
    db: AsyncSession = Depends(get_db),
    _user=Depends(_admin),
):
    """查询所有账户列表（需管理员）。"""
    result = await db.execute(select(Account))
    return [_to_out(a) for a in result.scalars().all()]


@router.get("/{account_id}", response_model=AccountOut)
async def get_account(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    _user=Depends(_admin),
):
    """查询单个账户详情（需管理员）。"""
    result = await db.execute(select(Account).where(Account.id == account_id))
    acct = result.scalar_one_or_none()
    if not acct:
        raise HTTPException(status_code=404, detail="账户不存在")
    return _to_out(acct)


def _to_out(acct) -> AccountOut:
    """将 Account 模型转换为响应模型。"""
    return AccountOut(
        id=acct.id,
        name=acct.name,
        slug=acct.slug,
        api_key=acct.api_key,
        is_active=acct.is_active,
        created_at=str(acct.created_at),
    )

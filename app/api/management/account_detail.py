"""账户详情与管理路由。

提供删除账户功能。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user_id
from app.models.account import Account
from app.models.session import get_db

router = APIRouter()


@router.post("/{account_id}/delete")
async def delete_account(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    _uid: str = Depends(get_current_user_id),
):
    """删除指定账户。"""
    acct = (
        await db.execute(select(Account).where(Account.id == account_id))
    ).scalar_one_or_none()
    if not acct:
        raise HTTPException(404, "账户不存在")
    acct.is_active = False
    await db.commit()
    return {"message": "账户已停用"}

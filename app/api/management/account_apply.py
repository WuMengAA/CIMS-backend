"""账户申请创建路由。

创建账户时 slug 自动随机生成。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.account import AccountCreate
from app.api.schemas.account_out import AccountOut
from app.core.auth.dependencies import get_current_user_id
from app.models.session import get_db
from app.models.user import User
from app.services.user.account_creator import create_account
from .account_helpers import _out

router = APIRouter()


@router.post("/apply", response_model=AccountOut, status_code=201)
async def apply_account(
    body: AccountCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """申请创建新账户（slug 自动生成）。"""
    user = (
        await db.execute(select(User).where(User.id == user_id))
    ).scalar_one_or_none()
    if not user or not user.can_create_account:
        raise HTTPException(status_code=403, detail="无权创建账户")
    try:
        account = await create_account(body.name, user_id, db, slug=body.slug)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _out(account)

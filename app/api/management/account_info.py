"""账户信息查询与 slug 修改路由。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.account_out import AccountOut
from app.api.schemas.profile import SlugUpdate
from app.core.auth.dependencies import get_current_user_id
from app.models.account import Account
from app.models.session import get_db
from app.services.user.account_service import update_account_slug
from .account_helpers import _out

router = APIRouter()


@router.get("/{account_id}/info", response_model=AccountOut)
async def get_account_info(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    _uid: str = Depends(get_current_user_id),
):
    """获取账户信息。"""
    acct = (
        await db.execute(select(Account).where(Account.id == account_id))
    ).scalar_one_or_none()
    if not acct:
        raise HTTPException(404, "账户不存在")
    return _out(acct)


@router.post("/{account_id}/info/slug", response_model=AccountOut)
async def change_slug(
    account_id: str,
    body: SlugUpdate,
    db: AsyncSession = Depends(get_db),
    uid: str = Depends(get_current_user_id),
):
    """修改账户 slug。"""
    try:
        acct = await update_account_slug(account_id, body.slug, uid, db)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except PermissionError as exc:
        raise HTTPException(403, str(exc))
    if not acct:
        raise HTTPException(404, "账户不存在")
    return _out(acct)

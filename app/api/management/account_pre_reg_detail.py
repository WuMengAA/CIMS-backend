"""预注册客户端详情路由。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import BASE_DOMAIN
from app.models.account import Account
from app.models.pre_registered_client import PreRegisteredClient
from app.models.session import get_db
from .account_pre_reg_crud import _to_out

router = APIRouter()


@router.get("/{pre_reg_id}")
async def get_pre_reg(
    account_id: str,
    pre_reg_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取预注册客户端信息。"""
    row = (
        await db.execute(
            select(PreRegisteredClient).where(
                PreRegisteredClient.id == pre_reg_id,
                PreRegisteredClient.account_id == account_id,
            )
        )
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(404, "预注册客户端不存在")
    return _to_out(row)


@router.post("/{pre_reg_id}/delete", status_code=204)
async def delete_pre_reg(
    account_id: str,
    pre_reg_id: str,
    db: AsyncSession = Depends(get_db),
):
    """删除预注册客户端。"""
    row = (
        await db.execute(
            select(PreRegisteredClient).where(
                PreRegisteredClient.id == pre_reg_id,
                PreRegisteredClient.account_id == account_id,
            )
        )
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(404, "预注册客户端不存在")
    await db.delete(row)
    await db.commit()

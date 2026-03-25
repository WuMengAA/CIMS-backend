"""访问控制（具权用户）管理路由。

列出、搜索、删除和修改具权用户的权限。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user_id
from app.models.account_member import AccountMember
from app.models.session import get_db

router = APIRouter()


@router.post("/list")
async def list_access(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    _uid: str = Depends(get_current_user_id),
):
    """列出账户下的具权用户。"""
    rows = (
        await db.execute(
            select(AccountMember).where(
                AccountMember.account_id == account_id
            )
        )
    ).scalars().all()
    return [
        {
            "user_id": m.user_id,
            "account_id": m.account_id,
            "role_code": m.role_code,
        }
        for m in rows
    ]

"""邀请管理路由。

提供邀请的列表、创建、搜索和详情管理。
"""

from fastapi import APIRouter, Depends
from app.core.auth.dependencies import get_current_user_id

router = APIRouter()


@router.post("/list")
async def list_invitations(
    account_id: str,
    _uid: str = Depends(get_current_user_id),
):
    """列出账户下的邀请。"""
    # 预留接口：邀请功能待后续实现
    return []


@router.post("/create")
async def create_invitation(
    account_id: str,
    _uid: str = Depends(get_current_user_id),
):
    """创建新邀请。"""
    return {"message": "邀请功能开发中"}

"""令牌刷新端点。

使用有效的会话令牌换取新令牌，延长会话有效期。
"""

from fastapi import APIRouter, Depends

from app.core.auth.dependencies import get_current_user_id
from app.services.crypto.token_factory import create_session_token

router = APIRouter()


@router.post("/refresh")
async def refresh_token(
    user_id: str = Depends(get_current_user_id),
):
    """刷新当前会话令牌。"""
    token = await create_session_token(user_id)
    return {"token": token}

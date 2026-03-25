"""令牌验证端点。

校验客户端持有的令牌是否仍然有效。
"""

from fastapi import APIRouter, Depends

from app.core.auth.dependencies import get_current_user_id

router = APIRouter()


@router.post("/verify")
async def verify_token(
    user_id: str = Depends(get_current_user_id),
):
    """验证当前令牌有效性，返回关联的用户 ID。"""
    return {"valid": True, "user_id": user_id}

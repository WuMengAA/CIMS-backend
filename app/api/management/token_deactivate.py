"""令牌注销端点。

销毁当前会话令牌，使其立即失效。
"""

from fastapi import APIRouter, Request

from app.api.schemas.auth import MessageResponse
from app.core.config import REDIS_DB_AUTH
from app.core.redis.accessor import get_redis

router = APIRouter()


@router.post("/deactivate", response_model=MessageResponse)
async def deactivate_token(request: Request):
    """注销当前会话令牌（登出）。"""
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        rd = get_redis(REDIS_DB_AUTH)
        await rd.delete(f"session:{auth[7:]}")
    return MessageResponse(message="已登出")

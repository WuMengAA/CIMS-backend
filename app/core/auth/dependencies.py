"""FastAPI 认证依赖项。

提供请求级别的用户身份解析、角色检查和权限验证，
作为路由处理器的可注入依赖使用。
"""

from typing import Optional

from fastapi import Request, HTTPException

from app.core.config import REDIS_DB_AUTH
from app.core.redis.accessor import get_redis
from app.models.user import User
from app.models.engine import AsyncSessionLocal

from sqlalchemy import select


async def get_current_user(request: Request) -> User:
    """从请求中解析当前已认证用户。

    Raises:
        HTTPException(401): 令牌无效或用户不存在。
    """
    user_id = getattr(request.state, "current_user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="未认证")
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def require_role(min_priority: int):
    """生成角色等级检查依赖。

    Args:
        min_priority: 最低角色优先级阈值。
    """

    async def _check(request: Request) -> User:
        """验证用户角色等级是否满足要求。"""
        user = await get_current_user(request)
        from app.models.custom_role import CustomRole

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(CustomRole).where(CustomRole.code == user.role_code)
            )
            role = result.scalar_one_or_none()
        priority = role.priority if role else 0
        if priority < min_priority:
            raise HTTPException(status_code=403, detail="权限不足")
        return user

    return _check


async def resolve_user_from_token(token: str) -> Optional[str]:
    """从 Redis 会话令牌解析用户 ID。"""
    rd = get_redis(REDIS_DB_AUTH)
    data = await rd.hgetall(f"session:{token}")
    return data.get("user_id") if data else None


async def get_current_user_id(request: Request) -> str:
    """从请求状态提取已认证的用户 ID（轻量依赖）。

    Raises:
        HTTPException(401): 未通过认证中间件。
    """
    uid = getattr(request.state, "current_user_id", None)
    if not uid:
        raise HTTPException(status_code=401, detail="未认证")
    return uid

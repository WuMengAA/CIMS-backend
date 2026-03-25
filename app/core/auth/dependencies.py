"""FastAPI 认证依赖项。

提供请求级别的用户身份解析、角色检查和权限验证，
作为路由处理器的可注入依赖使用。

所有需要数据库的依赖均通过 Depends(get_db) 注入会话，
FastAPI 会在同一请求内自动复用同一个 AsyncSession 实例，
避免多次连接池 Checkout。
"""

from typing import Optional

from fastapi import Depends, Request, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import REDIS_DB_AUTH
from app.core.redis.accessor import get_redis
from app.models.session import get_db
from app.models.user import User


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """从请求中解析当前已认证用户。

    通过 Depends(get_db) 注入会话，与路由处理器共享同一连接。

    Raises:
        HTTPException(401): 令牌无效或用户不存在。
    """
    user_id = getattr(request.state, "current_user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="未认证")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def require_role(min_priority: int):
    """生成角色等级检查依赖。

    内部通过 Depends(get_current_user) 获取用户，
    再利用同一个 db 会话查询角色，整个请求只使用一次连接。

    Args:
        min_priority: 最低角色优先级阈值。
    """

    async def _check(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        """验证用户角色等级是否满足要求。"""
        from app.models.custom_role import CustomRole

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

    此依赖不涉及数据库查询，仅从中间件注入的
    request.state.current_user_id 读取。

    Raises:
        HTTPException(401): 未通过认证中间件。
    """
    uid = getattr(request.state, "current_user_id", None)
    if not uid:
        raise HTTPException(status_code=401, detail="未认证")
    return uid

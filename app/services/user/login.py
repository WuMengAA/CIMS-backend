"""用户登录服务。

执行邮箱查找 → Argon2id 时间常量比对 →
角色状态检查 → TOTP 2FA 状态检查 → 生成会话令牌。
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.crypto.hasher import verify_password
from app.services.crypto.token_factory import create_session_token


async def login_user(
    email: str, password: str, db: AsyncSession
) -> tuple[str | None, User, bool]:
    """验证凭据并签发会话令牌（或标记需要 2FA）。

    Returns:
        (令牌|None, 用户, 是否需要2FA) 三元组。
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("邮箱或密码错误")
    _check_role_status(user)
    # 如果启用了 2FA，不直接签发令牌
    if user.totp_enabled:
        return None, user, True
    token = await create_session_token(user.id)
    return token, user, False


def _check_role_status(user: User) -> None:
    """检查用户全局角色是否允许登录。"""
    if user.role_code == "banned":
        raise ValueError("该账户已被封禁")
    if user.role_code == "pending":
        raise ValueError("该账户尚未激活")
    if not user.is_active:
        raise ValueError("该账户已被停用")

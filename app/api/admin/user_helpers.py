"""用户模型输出辅助。"""

from app.api.schemas.user_out import UserOut


def _to_out(user) -> UserOut:
    """将 User 模型转换为响应模型。"""
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        display_name=user.display_name,
        role_code=user.role_code,
        is_active=user.is_active,
        can_create_account=user.can_create_account,
        created_at=str(user.created_at),
    )

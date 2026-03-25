"""用户资料修改请求模型。

定义邮箱、用户名和密码变更的请求体。
"""

from pydantic import BaseModel, EmailStr, Field


class EmailUpdate(BaseModel):
    """邮箱修改请求体。"""

    email: EmailStr


class UsernameUpdate(BaseModel):
    """用户名修改请求体。"""

    username: str = Field(..., min_length=3, max_length=64)


class PasswordReset(BaseModel):
    """密码重置请求体（管理员操作）。"""

    new_password: str = Field(..., min_length=12, max_length=128)


class PasswordChange(BaseModel):
    """密码修改请求体（需旧密码）。"""

    old_password: str = Field(..., max_length=128)
    new_password: str = Field(..., min_length=12, max_length=128)


class SlugUpdate(BaseModel):
    """Slug 修改请求。"""

    slug: str = Field(..., min_length=3, max_length=64)

"""用户相关数据传输定义。

封装用户注册、登录请求和响应的 Pydantic 模型。
"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class UserRegisterRequest(BaseModel):
    """用户注册请求体。"""

    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., min_length=12, max_length=128)
    display_name: str = Field("", max_length=128)


class UserLoginRequest(BaseModel):
    """用户登录请求体。"""

    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., max_length=128)


class UserOut(BaseModel):
    """用户信息响应模型。"""

    id: str
    username: str
    email: str
    display_name: str
    role_code: str
    is_active: bool
    created_at: str


class UserUpdateRequest(BaseModel):
    """用户信息更新请求体。"""

    display_name: Optional[str] = Field(None, max_length=128)
    role_code: Optional[str] = Field(None, max_length=32)
    is_active: Optional[bool] = None

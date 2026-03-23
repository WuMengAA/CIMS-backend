"""账户相关数据传输定义。

封装账户创建、修改和响应的 Pydantic 模型。
"""

from typing import Optional
from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    """创建新账户的请求体。"""

    name: str = Field(..., max_length=128)
    slug: str = Field(..., min_length=3, max_length=64)


class AccountUpdate(BaseModel):
    """修改账户的请求体。"""

    name: Optional[str] = Field(None, max_length=128)
    slug: Optional[str] = Field(None, min_length=3, max_length=64)
    is_active: Optional[bool] = None


class AccountOut(BaseModel):
    """账户信息响应模型。"""

    id: str
    name: str
    slug: str
    api_key: str
    is_active: bool
    created_at: str

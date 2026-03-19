"""租户相关数据传输定义。

封装了创建、列表和修改学校/组织租户时使用的数据结构。
"""

from typing import Optional
from pydantic import BaseModel


class TenantCreate(BaseModel):
    """注册新租户的参数。"""

    name: str
    slug: str


class TenantUpdate(BaseModel):
    """修改现有租户的参数。"""

    name: Optional[str] = None
    slug: Optional[str] = None
    is_active: Optional[bool] = None


class TenantOut(BaseModel):
    """返回给客户端的租户信息响应模型。"""

    id: str
    name: str
    slug: str
    api_key: str
    is_active: bool
    created_at: str

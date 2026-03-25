"""账户信息响应模型。"""

from pydantic import BaseModel


class AccountOut(BaseModel):
    """账户信息响应模型。"""

    id: str
    name: str
    slug: str
    api_key: str
    is_active: bool
    created_at: str

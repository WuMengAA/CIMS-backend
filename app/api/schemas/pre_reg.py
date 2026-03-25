"""预注册客户端数据传输模型。"""

from pydantic import BaseModel, Field


class PreRegCreate(BaseModel):
    """预注册客户端创建请求。"""

    label: str = Field(..., max_length=128)
    class_identity: str = Field(..., max_length=64)


class PreRegOut(BaseModel):
    """预注册客户端响应。"""

    id: str
    account_id: str
    label: str
    class_identity: str
    created_at: str

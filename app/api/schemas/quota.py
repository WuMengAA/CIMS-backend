"""限额相关数据传输定义。

封装限额查询和设置的 Pydantic 模型。
"""

from pydantic import BaseModel, Field


class QuotaSetRequest(BaseModel):
    """设置限额上限的请求体。"""

    quota_key: str = Field(..., max_length=64)
    max_value: int = Field(..., ge=-1)


class QuotaOut(BaseModel):
    """限额信息响应模型。"""

    id: str
    account_id: str
    quota_key: str
    max_value: int
    current_value: int

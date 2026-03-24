"""统一响应模板。

定义 API 响应的标准成功/错误结构。
"""

from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    """写操作或指令接口的通用状态指示。"""

    status: str = Field(max_length=32)
    message: str = Field(max_length=1024)

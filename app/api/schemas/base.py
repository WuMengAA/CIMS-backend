"""统一响应模板。

定义 API 响应的标准成功/错误结构。
"""

from pydantic import BaseModel


class StatusResponse(BaseModel):
    """写操作或指令接口的通用状态指示。"""

    status: str
    message: str

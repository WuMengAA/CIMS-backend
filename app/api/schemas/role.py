"""角色分级相关数据传输定义。

封装角色创建、查询的 Pydantic 模型。
"""

from pydantic import BaseModel, Field


class RoleCreateRequest(BaseModel):
    """创建自定义角色的请求体。"""

    code: str = Field(..., min_length=2, max_length=32)
    label: str = Field(..., max_length=64)
    priority: int = Field(..., ge=-100, le=99)


class RoleOut(BaseModel):
    """角色信息响应模型。"""

    id: str
    code: str
    label: str
    priority: int
    is_system: bool

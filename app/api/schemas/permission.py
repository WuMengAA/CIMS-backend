"""权限相关数据传输定义。

封装权限定义查询和授予/撤销的 Pydantic 模型。
"""

from pydantic import BaseModel, Field


class PermissionGrantRequest(BaseModel):
    """权限授予/拒绝请求体。"""

    member_id: str = Field(..., description="成员 ID")
    permission_code: str = Field(..., max_length=64)
    granted: bool = Field(True, description="True=授予, False=拒绝")


class PermissionRevokeRequest(BaseModel):
    """权限撤销请求体。"""

    member_id: str = Field(..., description="成员 ID")
    permission_code: str = Field(..., max_length=64)


class PermissionDefOut(BaseModel):
    """权限定义响应模型。"""

    code: str
    label: str
    category: str

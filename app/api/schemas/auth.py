"""认证接口定义。

定义了管理端登录请求和响应的 JSON 结构。
"""

from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    """管理端登录请求体（包含 Secret）。"""

    secret: str = Field(..., description="The global admin secret.")


class TokenResponse(BaseModel):
    """颁发给管理端的令牌封装。"""

    token: str
    expires_in: int = 300
    token_type: str = "Bearer"

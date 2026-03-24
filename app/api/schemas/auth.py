"""认证接口定义。

定义用户登录响应和令牌封装数据结构。
"""

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """颁发给客户端的会话令牌封装。"""

    token: str = Field(max_length=512)
    expires_in: int = 3600
    token_type: str = Field(default="Bearer", max_length=32)


class MessageResponse(BaseModel):
    """通用消息响应模型。"""

    status: str = Field(default="success", max_length=32)
    message: str = Field(default="", max_length=1024)

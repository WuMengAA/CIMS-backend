"""认证接口定义。

定义用户登录响应和令牌封装数据结构。
"""

from pydantic import BaseModel


class TokenResponse(BaseModel):
    """颁发给客户端的会话令牌封装。"""

    token: str
    expires_in: int = 3600
    token_type: str = "Bearer"


class MessageResponse(BaseModel):
    """通用消息响应模型。"""

    status: str = "success"
    message: str = ""

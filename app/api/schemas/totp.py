"""2FA 数据传输模型。

定义 TOTP 启用、确认、验证和恢复的请求/响应。
"""

from pydantic import BaseModel


class TotpEnableResponse(BaseModel):
    """启用 2FA 响应：返回密钥和 URI。"""

    secret: str
    uri: str
    recovery_codes: list[str]


class TotpConfirmRequest(BaseModel):
    """确认绑定请求：提交 TOTP 码。"""

    code: str


class TotpVerifyRequest(BaseModel):
    """登录 2FA 验证请求。"""

    temp_token: str
    code: str


class TotpDisableRequest(BaseModel):
    """禁用 2FA 请求：需验证密码。"""

    password: str


class TotpRecoverRequest(BaseModel):
    """恢复码验证请求。"""

    temp_token: str
    recovery_code: str

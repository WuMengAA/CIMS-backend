"""2FA TOTP 路由。

提供启用、确认、禁用、登录验证和恢复码接口。
"""

from fastapi import APIRouter

router = APIRouter(prefix="/admin/auth/2fa", tags=["2fa"])

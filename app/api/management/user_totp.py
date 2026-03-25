"""Management API TOTP 路由。

复用 admin/totp_* 实现，挂载到 /user/2fa/totp 前缀。
"""

from fastapi import APIRouter

from app.api.admin.totp_routes import router as _totp_sub

# 导入以触发路由注册副作用
from app.api.admin import totp_enable, totp_confirm, totp_verify  # noqa: F401

router = APIRouter()
router.include_router(_totp_sub)

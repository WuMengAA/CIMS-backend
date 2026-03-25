"""超管平台级 API 聚合路由。

按 NewAPI.md 定义：/user/*、/user/pending/*、/account、/settings、/bulk。
"""

from fastapi import APIRouter

from .user_routes import router as user_list_r
from .user_create import router as user_create_r
from .user_detail import router as user_detail_r
from .user_delete import router as user_delete_r
from .user_password import router as user_pwd_r
from .admin_totp import router as totp_r
from .admin_totp_actions import router as totp_dis_r
from .admin_totp_reset import router as totp_rst_r
from .approval_routes import router as approval_r
from .account_routes import router as acct_r
from .settings import router as settings_r
from .admin_bulk import router as bulk_r

router = APIRouter()

# /user 用户管理
router.include_router(user_list_r, prefix="/user", tags=["User"])
router.include_router(user_create_r, prefix="/user", tags=["User"])
router.include_router(user_detail_r, prefix="/user", tags=["User"])
router.include_router(user_delete_r, prefix="/user", tags=["User"])
router.include_router(user_pwd_r, prefix="/user", tags=["User"])
router.include_router(totp_r, prefix="/user", tags=["2FA"])
router.include_router(totp_dis_r, prefix="/user", tags=["2FA"])
router.include_router(totp_rst_r, prefix="/user", tags=["2FA"])

# /user/pending 审核
router.include_router(approval_r, prefix="/user/pending", tags=["Pending"])

# /account 复用 Management 账户路由
router.include_router(acct_r, prefix="/account", tags=["Account"])

# /settings 系统设置
router.include_router(settings_r, prefix="/settings", tags=["Settings"])

# /bulk 批量操作
router.include_router(bulk_r, prefix="/bulk", tags=["Bulk"])

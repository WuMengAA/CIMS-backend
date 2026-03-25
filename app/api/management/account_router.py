"""Management API 账户级聚合路由。

挂载所有 /account/* 下的子路由。
"""

from fastapi import APIRouter

from .account_list import router as list_r
from .account_search import router as search_r
from .account_apply import router as apply_r
from .account_detail import router as detail_r
from .account_info import router as info_r
from .account_resource import router as res_r
from .account_client import router as cli_r
from .account_pairing import router as pair_r
from .account_pairing_action import router as pair_act_r
from .account_pre_reg_crud import router as prereg_r
from .account_pre_reg_detail import router as prereg_d_r
from .account_pre_reg_preset import router as prereg_p_r
from .account_access import router as access_r
from .account_invitation import router as inv_r
from .bulk import router as bulk_r
from app.api.command.router import router as cmd_r

router = APIRouter()

# /account 顶层
router.include_router(list_r, prefix="/account", tags=["Account"])
router.include_router(search_r, prefix="/account", tags=["Account"])
router.include_router(apply_r, prefix="/account", tags=["Account"])

# /account/{account_id}/*
router.include_router(detail_r, prefix="/account", tags=["Account"])
router.include_router(info_r, prefix="/account", tags=["Account"])

# 资源和客户端（需账户上下文）
_acct = "/accounts/{account_id}"
router.include_router(res_r, prefix=f"{_acct}", tags=["Resource"])
router.include_router(cli_r, prefix=f"{_acct}/client", tags=["Client"])

# 配对码
router.include_router(pair_r, prefix=f"{_acct}/pairing", tags=["Pairing"])
router.include_router(pair_act_r, prefix=f"{_acct}/pairing", tags=["Pairing"])

# 预注册
_pre = f"{_acct}/pre-registration"
router.include_router(prereg_r, prefix=_pre, tags=["PreReg"])
router.include_router(prereg_d_r, prefix=_pre, tags=["PreReg"])
router.include_router(prereg_p_r, prefix=_pre, tags=["PreReg"])

# 访问控制和邀请
router.include_router(access_r, prefix=f"{_acct}/access", tags=["Access"])
router.include_router(inv_r, prefix=f"{_acct}/invitation", tags=["Invite"])

# 批量操作
router.include_router(bulk_r, prefix="/account/bulk", tags=["Bulk"])

# 指令/数据操作
router.include_router(
    cmd_r, prefix=f"{_acct}/command", tags=["Command"]
)

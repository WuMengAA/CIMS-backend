"""账户客户端管理路由。

提供已连接客户端的列表、搜索、控制和状态查询。
复用 command 模块的客户端管理逻辑。
"""

from fastapi import APIRouter

from app.api.command.client_status import router as status_r
from app.api.command.client_control import router as control_r
from app.api.command.client_notification import router as notify_r
from app.api.command.client_config import router as config_r

router = APIRouter()

# 客户端监控与控制接口
router.include_router(status_r)
router.include_router(control_r)
router.include_router(notify_r)
router.include_router(config_r)

"""CIMS 后端服务主入口。

负责并发启动面向终端的 Client API 和面向管理的 Admin API。
"""

import asyncio
import logging
import uvicorn
from app.core.config import CLIENT_PORT, ADMIN_PORT
from app.apps.client_app import client_app
from app.apps.admin_app import admin_app

logger = logging.getLogger(__name__)


async def _start_servers():
    """并发运行两个独立的 uvicorn 实例。"""
    c_cfg = uvicorn.Config(client_app, host="0.0.0.0", port=CLIENT_PORT)
    a_cfg = uvicorn.Config(admin_app, host="0.0.0.0", port=ADMIN_PORT)

    logger.info("启动应用：Client:%d  Admin:%d", CLIENT_PORT, ADMIN_PORT)

    await asyncio.gather(uvicorn.Server(c_cfg).serve(), uvicorn.Server(a_cfg).serve())


def main():
    """主程序启动函数。"""
    try:
        asyncio.run(_start_servers())
    except KeyboardInterrupt:
        logger.info("系统已安全关闭")


if __name__ == "__main__":
    main()

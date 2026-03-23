"""全局应用生命周期管理。

控制数据库初始化、Redis 连接池分配以及 gRPC 服务器的启动与退出。
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.redis.pool import init_redis, close_redis
from app.models.database import init_db
from app.grpc.server.bootstrap import serve_grpc

logger = logging.getLogger(__name__)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """FastAPI 生命周期：随应用启动初始化核心后端服务。"""
    await init_db()
    await init_redis()

    # 启动 gRPC 服务器（拦截器在 bootstrap 中自动创建）
    grpc_s, cmd_s, sess_m = await serve_grpc()

    # 共享服务实例给 HTTP API 使用
    app.state.command_servicer = cmd_s
    app.state.session_manager = sess_m

    yield

    # 优雅停机
    if grpc_s:
        await grpc_s.stop(grace=5)
    await close_redis()
    logger.info("系统停机完成")

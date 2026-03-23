"""客户端 API 应用定义。

挂载面向终端设备的资源下载、Manifest 获取以及引导配置接口。
"""

from fastapi import FastAPI
from app.api.client.router import router as client_router
from app.api.client.token_get import router as token_get_router
from app.api.management_config.routes import router as mc_router
from app.core.auth.http_middleware import TenantMiddleware
from .lifespan import app_lifespan

# 客户端 App 实例（绑定全局生命周期）
client_app = FastAPI(title="CIMS 客户端 API", version="0.2.0", lifespan=app_lifespan)

client_app.add_middleware(TenantMiddleware)

# 挂载业务路由
client_app.include_router(client_router, prefix="/api", tags=["Client"])
client_app.include_router(mc_router, prefix="/api", tags=["Guide"])
client_app.include_router(token_get_router, tags=["TokenGet"])


@client_app.get("/")
async def root():
    """终端 API 状态检测。"""
    return {"message": "CIMS Backend is running"}

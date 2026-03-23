"""客户端 API 聚合路由。

将清单发现和资源访问端点聚合到客户端 API 应用的主路由中。
"""

from fastapi import APIRouter
from .manifest import router as manifest_router
from .resource import router as resource_router

router = APIRouter()

router.include_router(manifest_router)
router.include_router(resource_router)

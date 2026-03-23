"""FastAPI 数据库会话依赖项。

为请求处理器提供具有 Schema 隔离的异步数据库会话。
"""

from app.core.tenant.context import set_search_path
from .engine import AsyncSessionLocal


async def get_db():
    """生成异步数据库会话，按租户 Schema 设置 search_path。"""
    async with AsyncSessionLocal() as session:
        await set_search_path(session)
        yield session

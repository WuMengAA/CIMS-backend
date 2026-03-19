"""SQLAlchemy 引擎与会话工厂配置。

配置异步 PostgreSQL 引擎，并提供表初始化辅助函数。
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import DATABASE_URL
from .base import Base

# Engine configuration (asyncpg/psycopg-based)
engine = create_async_engine(DATABASE_URL, echo=False, pool_size=10, max_overflow=20)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """初始化连接数据库中的所有表。"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

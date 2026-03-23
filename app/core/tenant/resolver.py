"""账户解析逻辑，协调 Redis 缓存与 PostgreSQL。

根据 Slug（二级域名标识）安全查找账户的主要接口。
"""

from typing import Optional, TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .cache import get_cached_account, set_cached_account

if TYPE_CHECKING:
    from app.models.account import Account


async def resolve_account(slug: str, db: AsyncSession) -> Optional["Account"]:
    """根据 slug 解析账户，优先缓存，其次数据库。"""
    account = await get_cached_account(slug)
    if account is not None:
        return account if account.is_active else None
    # 数据库查找（延迟导入避免循环依赖）
    from app.models.account import Account

    stmt = select(Account).where(Account.slug == slug)
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()
    if account and account.is_active:
        await set_cached_account(slug, account)
        return account
    return None

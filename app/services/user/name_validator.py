"""用户名/Slug 格式校验与保留名检查。

Username: 3~64 位 [a-z0-9_]
Slug: 3~64 位 [a-z0-9-]（减号替代下划线）
两者共享命名空间，与保留名互斥。
"""

import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reserved_name import ReservedName

# 编译一次，复用正则
_USERNAME_RE = re.compile(r"^[a-z0-9_]{3,64}$")
_SLUG_RE = re.compile(r"^[a-z0-9\-]{3,64}$")


def validate_username_format(name: str) -> bool:
    """校验用户名格式是否合法。"""
    return bool(_USERNAME_RE.match(name))


def validate_slug_format(slug: str) -> bool:
    """校验 Slug 格式是否合法。"""
    return bool(_SLUG_RE.match(slug))


async def is_name_reserved(name: str, db: AsyncSession) -> bool:
    """检查名称是否被系统保留。"""
    result = await db.execute(
        select(ReservedName).where(ReservedName.name == name.lower())
    )
    return result.scalar_one_or_none() is not None

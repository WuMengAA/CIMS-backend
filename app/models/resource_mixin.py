"""租户范围内资源文件模型的共有字段。

为按 (tenant, name) 索引、存储 JSON 内容及版本的表提供通用结构。
"""

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class ResourceMixin:
    """资源存储表的模型 Mixin。"""

    tenant_id: Mapped[str] = mapped_column(
        String, ForeignKey("tenants.id"), primary_key=True
    )
    name: Mapped[str] = mapped_column(String, primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

"""账户（Account）实体定义。

替代原 Tenant 模型，存储组织/学校的元数据与 API 密钥。
账户无"所有者"字段——所有权通过 AccountMember 角色体现。
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Account(Base):
    """账户（组织/租户）身份与配置记录。"""

    __tablename__ = "accounts"

    # UUID4 主键
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # 组织名称
    name: Mapped[str] = mapped_column(String(128))
    # URL 标识：3~64 位 [a-z0-9-]
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    # API 密钥
    api_key: Mapped[str] = mapped_column(String(256))
    # 启用状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # 创建时间
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

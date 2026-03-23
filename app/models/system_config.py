"""系统配置持久化。

元数据数据库中的键值对配置表，
OOBE 初始化后所有非数据库连接的配置均存于此。
"""

from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class SystemConfig(Base):
    """系统级键值配置记录。"""

    __tablename__ = "system_config"

    # 配置键（主键）
    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    # 配置值
    value: Mapped[str] = mapped_column(Text, default="")
    # 最后更新时间
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

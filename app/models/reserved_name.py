"""保留名称注册表。

存储系统保留的 Username 和 Slug，
防止用户注册时占用关键系统标识符。
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ReservedName(Base):
    """系统保留名称记录。"""

    __tablename__ = "reserved_names"

    # 保留名（主键，全小写）
    name: Mapped[str] = mapped_column(String(64), primary_key=True)
    # 保留原因
    reason: Mapped[str] = mapped_column(String(128), default="system")

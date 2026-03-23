"""审计日志模型实现。

记录客户端事件和状态变更，供管理控制台查阅。
Schema 隔离后不再需要 tenant_id 列。
"""

from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class AuditLog(Base):
    """客户端设备事件日志的持久化存储。"""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    client_uid: Mapped[str] = mapped_column(String)
    event: Mapped[int] = mapped_column(Integer)
    payload: Mapped[str] = mapped_column(Text)
    timestamp_utc: Mapped[int] = mapped_column(Integer)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

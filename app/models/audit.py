"""Audit logging model implementation.

Records client events and state changes for management visibility.
"""

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class AuditLog(Base):
    """Permanent storage for client device event logs."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String, ForeignKey("tenants.id"))
    client_uid: Mapped[str] = mapped_column(String)
    event: Mapped[int] = mapped_column(Integer)
    payload: Mapped[str] = mapped_column(Text)
    timestamp_utc: Mapped[int] = mapped_column(Integer)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

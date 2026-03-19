"""Configuration upload model.

Stores serialized snapshots of client configurations for debugging and backup.
"""

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class ConfigUploadRecord(Base):
    """Temporary storage for uploaded client config blobs."""

    __tablename__ = "config_uploads"

    tenant_id: Mapped[str] = mapped_column(
        String, ForeignKey("tenants.id"), primary_key=True
    )
    request_guid: Mapped[str] = mapped_column(String, primary_key=True)
    client_uid: Mapped[str] = mapped_column(String)
    payload: Mapped[str] = mapped_column(Text)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

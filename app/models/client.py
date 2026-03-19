"""Client registration and profile models.

Stores hardware identification (MAC) and linked configuration
profiles for individual ClassIsland endpoints.
"""

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class ClientRecord(Base):
    """Database record for a registered physical client device."""

    __tablename__ = "clients"

    tenant_id: Mapped[str] = mapped_column(
        String, ForeignKey("tenants.id"), primary_key=True
    )
    uid: Mapped[str] = mapped_column(String, primary_key=True)
    client_id: Mapped[str] = mapped_column(String, default="")
    mac: Mapped[str] = mapped_column(String, default="")
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ClientProfile(Base):
    """Relationship mapping a client to specific resource files."""

    __tablename__ = "client_profiles"

    tenant_id: Mapped[str] = mapped_column(
        String, ForeignKey("tenants.id"), primary_key=True
    )
    client_id: Mapped[str] = mapped_column(String, primary_key=True)
    class_plan: Mapped[str] = mapped_column(String)
    time_layout: Mapped[str] = mapped_column(String)
    subjects: Mapped[str] = mapped_column(String)
    default_settings: Mapped[str] = mapped_column(String)
    policy: Mapped[str] = mapped_column(String)
    components: Mapped[str] = mapped_column(String, nullable=True)
    credentials: Mapped[str] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

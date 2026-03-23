"""配置上报模型。

存储客户端配置的序列化快照，用于调试和备份。
Schema 隔离后不再需要 tenant_id 列。
"""

from datetime import datetime
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class ConfigUploadRecord(Base):
    """已上传客户端配置数据的临时存储。"""

    __tablename__ = "config_uploads"

    request_guid: Mapped[str] = mapped_column(String, primary_key=True)
    client_uid: Mapped[str] = mapped_column(String)
    payload: Mapped[str] = mapped_column(Text)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

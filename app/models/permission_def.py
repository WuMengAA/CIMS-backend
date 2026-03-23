"""原子权限定义。

存储系统中所有可分配的细粒度权限条目，
每条记录代表一个不可再分的操作权限。
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class PermissionDef(Base):
    """原子权限定义记录。"""

    __tablename__ = "permission_defs"

    # 权限编码（主键，如 client.read）
    code: Mapped[str] = mapped_column(String(64), primary_key=True)
    # 权限显示名
    label: Mapped[str] = mapped_column(String(128))
    # 权限分类（如 client / command / config）
    category: Mapped[str] = mapped_column(String(32), default="general")

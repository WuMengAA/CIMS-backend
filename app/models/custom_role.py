"""自定义角色分级定义。

存储系统内置和超级管理员自定义的角色分级，
通过 priority 字段确定等级高低排序。
"""

import uuid

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class CustomRole(Base):
    """角色分级记录（含系统内置与自定义）。"""

    __tablename__ = "custom_roles"

    # UUID4 主键
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # 角色编码（唯一标识符）
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    # 角色显示名
    label: Mapped[str] = mapped_column(String(64))
    # 优先级数值（越高权限越大）
    priority: Mapped[int] = mapped_column(Integer, default=0)
    # 是否系统内置（不可删除）
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)

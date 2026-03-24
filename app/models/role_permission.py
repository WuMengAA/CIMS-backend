"""角色-权限多对多关联。

将角色编码与权限编码关联，实现 RBAC 的角色权限分配。
"""

import uuid

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class RolePermission(Base):
    """角色与原子权限的关联记录。"""

    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_code", "permission_code", name="uq_role_perm"),
    )

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # 关联角色编码
    role_code: Mapped[str] = mapped_column(String(32), index=True)
    # 关联权限编码
    permission_code: Mapped[str] = mapped_column(String(64))

"""成员级权限覆盖定义。

存储对特定 AccountMember 的逐项权限授予/拒绝记录，
实现超细粒度的原子级权限控制。
"""

import uuid

from sqlalchemy import Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class MemberPermission(Base):
    """成员粒度的权限覆盖记录。"""

    __tablename__ = "member_permissions"
    __table_args__ = (
        UniqueConstraint("member_id", "permission_code", name="uq_member_perm"),
    )

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # 关联的 AccountMember ID
    member_id: Mapped[str] = mapped_column(String, index=True)
    # 关联的权限编码
    permission_code: Mapped[str] = mapped_column(String(64))
    # 是否授予（True=允许, False=显式拒绝）
    granted: Mapped[bool] = mapped_column(Boolean, default=True)

"""用户-账户成员关系定义。

存储用户在特定账户中的成员身份与账户内角色，
参考 GitHub Organization 的 Owner/Admin/Member 模型。
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class AccountMember(Base):
    """用户在账户中的成员关系记录。"""

    __tablename__ = "account_members"
    __table_args__ = (
        UniqueConstraint("user_id", "account_id", name="uq_user_account"),
    )

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # 关联用户
    user_id: Mapped[str] = mapped_column(String, index=True)
    # 关联账户
    account_id: Mapped[str] = mapped_column(String, index=True)
    # 账户内角色：owner / admin / member / viewer
    role_in_account: Mapped[str] = mapped_column(String(32), default="member")
    # 加入时间
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

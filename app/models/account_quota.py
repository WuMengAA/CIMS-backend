"""账户限额定义。

存储每个账户的细粒度资源配额，
包括客户端数量、流量限制和功能开关。
"""

import uuid

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class AccountQuota(Base):
    """账户级资源限额记录。"""

    __tablename__ = "account_quotas"
    __table_args__ = (
        UniqueConstraint("account_id", "quota_key", name="uq_acct_quota"),
    )

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # 关联的账户 ID
    account_id: Mapped[str] = mapped_column(String, index=True)
    # 限额键名（如 max_clients, max_bandwidth_mb）
    quota_key: Mapped[str] = mapped_column(String(64))
    # 上限值（-1 表示无限制）
    max_value: Mapped[int] = mapped_column(Integer, default=-1)
    # 当前使用量
    current_value: Mapped[int] = mapped_column(Integer, default=0)

"""预注册客户端模型。

管理员在账户下预创建客户端条目（设定 class_identity），
ClassIsland 客户端加入集控时通过填入的 ClassIdentity 匹配。
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class PreRegisteredClient(Base):
    """预注册客户端记录。"""

    __tablename__ = "pre_registered_clients"

    # UUID4 主键
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # 所属账户 ID
    account_id: Mapped[str] = mapped_column(String, index=True)
    # 显示标签（如 "三年一班"）
    label: Mapped[str] = mapped_column(String(128))
    # 班级标识符 / 匹配键（如 "3-1"）
    class_identity: Mapped[str] = mapped_column(String(64), index=True)
    # 创建时间
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

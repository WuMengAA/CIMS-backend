"""用户（User）实体定义。

存储系统中的独立用户身份信息，
包括登录凭据、全局角色和账户状态。
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    """用户身份与凭据记录。"""

    __tablename__ = "users"

    # UUID4 主键
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # 用户名：3~64 位 [a-z0-9_]
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    # 邮箱（唯一索引）
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    # Argon2id 密码哈希
    hashed_password: Mapped[str] = mapped_column(String(512))
    # 显示名称
    display_name: Mapped[str] = mapped_column(String(128), default="")
    # 全局角色编码（关联 CustomRole.code）
    role_code: Mapped[str] = mapped_column(String(32), default="normal")
    # 账户启用状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # TOTP 双因素认证密钥（启用后存在）
    totp_secret: Mapped[str | None] = mapped_column(
        String(64), nullable=True, default=None
    )
    # 是否启用 TOTP 2FA
    totp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    # 创建时间
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

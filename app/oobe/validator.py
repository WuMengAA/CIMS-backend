"""OOBE 输入验证器。

校验 URL 格式、邮箱格式、密码强度和用户名格式。
"""

import re

# 密码强度要求：≥12字符，含大小写+数字+特殊字符
_PW_MIN_LEN = 12
_PW_UPPER = re.compile(r"[A-Z]")
_PW_LOWER = re.compile(r"[a-z]")
_PW_DIGIT = re.compile(r"[0-9]")
_PW_SPECIAL = re.compile(r"[^A-Za-z0-9]")

# 邮箱格式
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# 用户名格式
_USERNAME_RE = re.compile(r"^[a-z0-9_]{3,64}$")


def validate_db_url(url: str) -> str | None:
    """校验数据库连接 URL 格式。"""
    if not url.startswith(("postgresql", "postgres")):
        return "数据库 URL 必须以 postgresql 开头"
    return None


def validate_email(email: str) -> str | None:
    """校验邮箱格式。"""
    if not _EMAIL_RE.match(email):
        return "邮箱格式不合法"
    return None


def validate_password(pw: str) -> str | None:
    """校验密码强度。"""
    if len(pw) < _PW_MIN_LEN:
        return f"密码长度不得少于 {_PW_MIN_LEN} 位"
    if not _PW_UPPER.search(pw):
        return "密码必须包含大写字母"
    if not _PW_LOWER.search(pw):
        return "密码必须包含小写字母"
    if not _PW_DIGIT.search(pw):
        return "密码必须包含数字"
    if not _PW_SPECIAL.search(pw):
        return "密码必须包含特殊字符"
    return None


def validate_username(name: str) -> str | None:
    """校验用户名格式。"""
    if not _USERNAME_RE.match(name):
        return "用户名需为 3~64 位小写字母数字下划线"
    return None

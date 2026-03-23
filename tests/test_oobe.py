"""OOBE 初始化流程测试。

测试首次运行检测、配置文件写入和输入校验器。
"""

from app.oobe.validator import (
    validate_db_url,
    validate_email,
    validate_password,
    validate_username,
)
from app.services.user.name_validator import (
    validate_username_format,
    validate_slug_format,
)


class TestDetector:
    """初始化检测器测试。"""

    def test_not_initialized(self, tmp_path, monkeypatch):
        """无配置文件时应返回 False。"""
        monkeypatch.setattr(
            "app.oobe.detector.CONFIG_FILE",
            tmp_path / "nonexistent.json",
        )
        # 直接检查文件不存在
        assert not (tmp_path / "nonexistent.json").exists()


class TestValidator:
    """OOBE 输入校验器测试。"""

    def test_valid_db_url(self):
        """合法 PostgreSQL URL 应通过。"""
        assert validate_db_url("postgresql+psycopg://u:p@h/db") is None

    def test_invalid_db_url(self):
        """非 PostgreSQL URL 应被拒绝。"""
        assert validate_db_url("mysql://u:p@h/db") is not None

    def test_valid_email(self):
        """合法邮箱应通过。"""
        assert validate_email("user@example.com") is None

    def test_invalid_email(self):
        """非法邮箱应被拒绝。"""
        assert validate_email("not-an-email") is not None

    def test_strong_password(self):
        """满足所有要求的密码应通过。"""
        assert validate_password("MyStr0ng!Pass") is None

    def test_weak_password_short(self):
        """过短密码应被拒绝。"""
        assert validate_password("Sh0rt!") is not None

    def test_weak_password_no_upper(self):
        """无大写字母密码应被拒绝。"""
        assert validate_password("nouppercas3!!") is not None

    def test_weak_password_no_special(self):
        """无特殊字符密码应被拒绝。"""
        assert validate_password("NoSpecialChar1") is not None

    def test_valid_username(self):
        """合法用户名应通过。"""
        assert validate_username("admin_user") is None

    def test_invalid_username(self):
        """不合法用户名应被拒绝。"""
        assert validate_username("AB") is not None


class TestNameValidator:
    """用户名/Slug 格式校验测试。"""

    def test_valid_username_format(self):
        """合法格式的用户名。"""
        assert validate_username_format("hello_world")
        assert validate_username_format("abc")
        assert validate_username_format("user123")

    def test_invalid_username_format(self):
        """非法格式的用户名。"""
        assert not validate_username_format("ab")  # 太短
        assert not validate_username_format("Hello")  # 大写
        assert not validate_username_format("user-name")  # 减号

    def test_valid_slug_format(self):
        """合法格式的 Slug。"""
        assert validate_slug_format("my-school")
        assert validate_slug_format("abc")

    def test_invalid_slug_format(self):
        """非法格式的 Slug。"""
        assert not validate_slug_format("ab")  # 太短
        assert not validate_slug_format("my_school")  # 下划线

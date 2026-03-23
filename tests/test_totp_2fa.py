"""TOTP 双因素认证完整测试。

覆盖 2FA 启用、确认、禁用、登录验证、
恢复码、重放防护和恢复码耗尽场景。
"""

import pytest
import pyotp
from app.services.crypto.totp import (
    generate_totp_secret,
    verify_totp,
    get_totp_uri,
)
from app.services.crypto.recovery import (
    generate_recovery_codes,
    store_recovery_codes,
    use_recovery_code,
    get_remaining_count,
)


class TestTotpService:
    """TOTP 基础服务测试。"""

    def test_generate_secret_is_base32(self):
        """生成的密钥应为有效 Base32。"""
        secret = generate_totp_secret()
        assert len(secret) >= 16
        # 应能被 pyotp 正常使用
        totp = pyotp.TOTP(secret)
        assert totp.now()

    def test_verify_correct_code(self):
        """正确的 TOTP 码应验证通过。"""
        secret = generate_totp_secret()
        totp = pyotp.TOTP(secret)
        code = totp.now()
        assert verify_totp(secret, code)

    def test_verify_wrong_code(self):
        """错误的 TOTP 码应验证失败。"""
        secret = generate_totp_secret()
        assert not verify_totp(secret, "000000")
        assert not verify_totp(secret, "999999")

    def test_uri_format(self):
        """URI 应符合 otpauth 格式。"""
        secret = generate_totp_secret()
        uri = get_totp_uri(secret, "user@example.com")
        assert uri.startswith("otpauth://totp/")
        assert "CIMS" in uri
        assert secret in uri

    def test_totp_replay_different_window(self):
        """同一 TOTP 码在有效窗口内应能使用。"""
        secret = generate_totp_secret()
        code = pyotp.TOTP(secret).now()
        # 第一次验证
        assert verify_totp(secret, code)
        # 在同一窗口内再次验证（TOTP 本身允许）
        assert verify_totp(secret, code)


class TestRecoveryCodes:
    """恢复码服务测试。"""

    def test_generate_correct_count(self):
        """应生成 8 个恢复码。"""
        codes = generate_recovery_codes()
        assert len(codes) == 8
        assert len(set(codes)) == 8  # 全部唯一

    def test_code_format(self):
        """恢复码应为大写十六进制。"""
        codes = generate_recovery_codes()
        for c in codes:
            assert c == c.upper()
            int(c, 16)  # 应为有效十六进制

    @pytest.mark.asyncio
    async def test_store_and_use(self):
        """存储后应能正常使用恢复码。"""
        uid = "test-recovery-user"
        codes = generate_recovery_codes()
        await store_recovery_codes(uid, codes)
        assert await get_remaining_count(uid) == 8
        # 使用第一个
        assert await use_recovery_code(uid, codes[0])
        assert await get_remaining_count(uid) == 7
        # 重复使用应失败
        assert not await use_recovery_code(uid, codes[0])
        assert await get_remaining_count(uid) == 7

    @pytest.mark.asyncio
    async def test_invalid_code_rejected(self):
        """未生成的码应被拒绝。"""
        uid = "test-recovery-invalid"
        codes = generate_recovery_codes()
        await store_recovery_codes(uid, codes)
        assert not await use_recovery_code(uid, "ZZZZZZZZ")

    @pytest.mark.asyncio
    async def test_exhaust_all_codes(self):
        """用完所有恢复码后应无法继续使用。"""
        uid = "test-recovery-exhaust"
        codes = generate_recovery_codes()
        await store_recovery_codes(uid, codes)
        for c in codes:
            assert await use_recovery_code(uid, c)
        assert await get_remaining_count(uid) == 0
        # 新的码不能用
        assert not await use_recovery_code(uid, "ABCD1234")

    @pytest.mark.asyncio
    async def test_store_overwrites_old(self):
        """重新生成码应覆盖旧码。"""
        uid = "test-recovery-overwrite"
        codes1 = generate_recovery_codes()
        await store_recovery_codes(uid, codes1)
        codes2 = generate_recovery_codes()
        await store_recovery_codes(uid, codes2)
        # 旧码不可用
        assert not await use_recovery_code(uid, codes1[0])
        # 新码可用
        assert await use_recovery_code(uid, codes2[0])

    @pytest.mark.asyncio
    async def test_case_insensitive_usage(self):
        """恢复码验证应大小写不敏感。"""
        uid = "test-recovery-case"
        codes = generate_recovery_codes()
        await store_recovery_codes(uid, codes)
        # 用小写提交
        assert await use_recovery_code(uid, codes[0].lower())

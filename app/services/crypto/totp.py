"""TOTP 双因素认证服务。

基于 pyotp 实现 TOTP 生成、验证和 URI 构建，
符合 RFC 6238 标准，兼容 Google Authenticator 等应用。
"""

import pyotp


def generate_totp_secret() -> str:
    """生成 Base32 编码的 TOTP 密钥。"""
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str) -> str:
    """构建 otpauth URI（用于二维码扫描）。

    Args:
        secret: Base32 编码密钥。
        email: 用户邮箱（作为标签）。

    Returns:
        otpauth://totp/... 格式 URI。
    """
    return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name="CIMS")


def verify_totp(secret: str, code: str) -> bool:
    """验证 TOTP 码，允许 ±30 秒时间偏移。"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)

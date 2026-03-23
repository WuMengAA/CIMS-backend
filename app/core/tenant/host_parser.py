"""HTTP 主机名中的租户标识提取。

提供从各种 Host 头格式中确定租户 Slug 的工具函数。
"""

from typing import Optional
from app.core.config import BASE_DOMAIN


def extract_slug_from_host(host: str) -> Optional[str]:
    """从 Host 头值中解析租户 Slug。

    Args:
        host: 请求中的主机字符串（例如 'tenant.cims.com:50050'）。

    Returns:
        提取到的 Slug（子域名部分），若为根域名则返回 None。
    """
    hostname = host.split(":")[0].lower()
    base = BASE_DOMAIN.lower()

    if not hostname.endswith(f".{base}"):
        return None

    slug = hostname[: -(len(base) + 1)]
    return slug if slug else None

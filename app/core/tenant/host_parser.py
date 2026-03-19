"""Tenant identifier extraction from HTTP hostname.

Utility functions to determine the tenant slug from various host header formats.
"""

from typing import Optional
from app.core.config import BASE_DOMAIN


def extract_slug_from_host(host: str) -> Optional[str]:
    """Parse a Host header value to find the tenant slug.

    Args:
        host: The host string from the request (e.g., 'tenant.cims.com:50050').

    Returns:
        The extracted slug (subdomain portion) or None if it's the root domain.
    """
    hostname = host.split(":")[0].lower()
    base = BASE_DOMAIN.lower()

    if not hostname.endswith(f".{base}"):
        return None

    slug = hostname[: -(len(base) + 1)]
    return slug if slug else None

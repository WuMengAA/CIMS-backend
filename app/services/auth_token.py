"""384-bit Token authentication service — Redis-backed.

Generates cryptographically secure tokens for API authentication.
Each token acts as both Access Token and Refresh Token with a sliding
TTL window that resets on every successful validation.
"""

import logging
import secrets
from typing import Optional

from app.core.redis import get_redis

logger = logging.getLogger(__name__)

# 384-bit = 48 bytes; token_urlsafe produces base64url (~64 chars)
_TOKEN_BYTES = 48
_DEFAULT_TTL = 300  # 5 minutes


async def generate_token(
    scope: str,
    tenant_id: str = "",
    *,
    ttl: int = _DEFAULT_TTL,
) -> str:
    """Generate a 384-bit auth token and store in Redis.

    Args:
        scope: Token scope — ``"admin"`` or ``"command"``.
        tenant_id: Tenant this token is scoped to (empty for admin).
        ttl: Time-to-live in seconds (default 300 = 5 min).
    """
    rd = get_redis()
    token = secrets.token_urlsafe(_TOKEN_BYTES)
    key = f"auth:{token}"
    await rd.hset(
        key,
        mapping={
            "scope": scope,
            "tenant_id": tenant_id,
        },
    )
    await rd.expire(key, ttl)
    logger.info(
        "Auth token created: scope=%s tenant=%s", scope, tenant_id or "(global)"
    )
    return token


async def validate_and_refresh(
    token: str,
    *,
    ttl: int = _DEFAULT_TTL,
) -> Optional[tuple[str, str]]:
    """Validate a token and refresh its TTL (sliding window).

    Returns:
        ``(scope, tenant_id)`` if valid, ``None`` otherwise.
    """
    if not token:
        return None
    rd = get_redis()
    key = f"auth:{token}"
    data = await rd.hgetall(key)
    if not data:
        return None

    # Refresh TTL on every successful validation
    await rd.expire(key, ttl)
    return (data["scope"], data.get("tenant_id", ""))


async def revoke_token(token: str) -> bool:
    """Revoke (delete) a token. Returns True if it existed."""
    if not token:
        return False
    rd = get_redis()
    deleted = await rd.delete(f"auth:{token}")
    return deleted > 0

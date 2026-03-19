"""Token-based resource access manager — backed by Redis.

Each token is stored as a Redis hash with TTL-based expiry and usage limits.
Tokens are scoped to a tenant.
"""

import logging
import secrets

from app.core.redis import get_redis

logger = logging.getLogger(__name__)

_TOKEN_LENGTH = 64
_DEFAULT_TTL = 300  # 5 minutes
_DEFAULT_MAX_USES = 1


async def create_token(
    tenant_id: str,
    resource_type: str,
    name: str,
    *,
    ttl: int = _DEFAULT_TTL,
    max_uses: int = _DEFAULT_MAX_USES,
    client_ip: str = "",
) -> str:
    """Create a token in Redis that resolves to a tenant-scoped resource."""
    rd = get_redis()
    token = secrets.token_urlsafe(_TOKEN_LENGTH)
    key = f"token:{token}"
    await rd.hset(
        key,
        mapping={
            "tenant_id": tenant_id,
            "resource_type": resource_type,
            "name": name,
            "remaining_uses": str(max_uses),
            "client_ip": client_ip,
        },
    )
    await rd.expire(key, ttl)
    return token


async def resolve_token(token: str) -> tuple[str, str, str, str] | None:
    """Resolve a token to (tenant_id, resource_type, name, client_ip), or None.

    Decrements usage counter; deletes the key when exhausted.
    """
    rd = get_redis()
    key = f"token:{token}"
    data = await rd.hgetall(key)
    if not data:
        return None

    remaining = int(data["remaining_uses"]) - 1
    if remaining <= 0:
        await rd.delete(key)
    else:
        await rd.hset(key, "remaining_uses", str(remaining))

    return (
        data["tenant_id"],
        data["resource_type"],
        data["name"],
        data.get("client_ip", ""),
    )

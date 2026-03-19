"""Tests for admin tenant CRUD, auth middleware, tenant resolution,
management config endpoint, and remaining coverage gaps.

Target: all uncovered lines in admin.py, auth.py, tenant.py, management_config.py,
client.py, server.py, session_manager.py, resource_token.py, redis.py.
"""

import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient, ASGITransport

from app.main import client_app, admin_app
from app.core.tenant import (
    extract_slug_from_host,
    resolve_tenant,
    get_tenant_id,
)
from app.models.database import AsyncSessionLocal, Tenant
from app.core.redis import get_redis

from tests.conftest import TEST_TENANT_ID, TEST_TENANT_SLUG


@pytest_asyncio.fixture(autouse=True)
async def lifespan():
    async with client_app.router.lifespan_context(client_app):
        admin_app.state.command_servicer = getattr(
            client_app.state, "command_servicer", None
        )
        admin_app.state.session_manager = getattr(
            client_app.state, "session_manager", None
        )
        yield


def _uniq(prefix: str = "t") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


async def _admin_headers() -> dict:
    """Helper: get a fresh admin token via login."""
    from app.services.auth_token import generate_token

    token = await generate_token("admin")
    return {"Authorization": f"Bearer {token}"}


async def _command_headers() -> dict:
    """Helper: get a fresh command token for the test tenant."""
    from app.services.auth_token import generate_token

    token = await generate_token("command", tenant_id=TEST_TENANT_ID)
    return {"Authorization": f"Bearer {token}"}


# ===========================================================================
# Admin API CRUD — full coverage of admin.py
# ===========================================================================


@pytest.mark.asyncio
async def test_admin_create_tenant():
    slug = _uniq("create")
    h = await _admin_headers()
    transport = ASGITransport(app=admin_app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        res = await ac.post(
            "/admin/tenants",
            headers=h,
            json={"name": "New School", "slug": slug},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["name"] == "New School"
        assert data["slug"] == slug
        assert data["is_active"] is True
        assert len(data["api_key"]) > 0


@pytest.mark.asyncio
async def test_admin_create_tenant_duplicate_slug():
    slug = _uniq("dup")
    h = await _admin_headers()
    transport = ASGITransport(app=admin_app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        await ac.post("/admin/tenants", headers=h, json={"name": "A", "slug": slug})
        res = await ac.post(
            "/admin/tenants", headers=h, json={"name": "B", "slug": slug}
        )
        assert res.status_code == 409


@pytest.mark.asyncio
async def test_admin_list_tenants():
    h = await _admin_headers()
    transport = ASGITransport(app=admin_app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        res = await ac.get("/admin/tenants", headers=h)
        assert res.status_code == 200
        assert isinstance(res.json(), list)
        assert len(res.json()) >= 1


@pytest.mark.asyncio
async def test_admin_get_tenant():
    h = await _admin_headers()
    transport = ASGITransport(app=admin_app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        res = await ac.get(f"/admin/tenants/{TEST_TENANT_ID}", headers=h)
        assert res.status_code == 200
        assert res.json()["id"] == TEST_TENANT_ID

        res = await ac.get("/admin/tenants/nonexistent-id", headers=h)
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_admin_update_tenant():
    """Cover admin.py L86-100: update name, slug, is_active."""
    slug = _uniq("upd")
    h = await _admin_headers()
    transport = ASGITransport(app=admin_app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        create_res = await ac.post(
            "/admin/tenants", headers=h, json={"name": "Upd", "slug": slug}
        )
        tid = create_res.json()["id"]

        # Update name only
        res = await ac.put(f"/admin/tenants/{tid}", headers=h, json={"name": "NewName"})
        assert res.status_code == 200
        assert res.json()["name"] == "NewName"

        # Update slug
        new_slug = _uniq("upd2")
        res = await ac.put(f"/admin/tenants/{tid}", headers=h, json={"slug": new_slug})
        assert res.status_code == 200
        assert res.json()["slug"] == new_slug

        # Update is_active
        res = await ac.put(
            f"/admin/tenants/{tid}", headers=h, json={"is_active": False}
        )
        assert res.status_code == 200
        assert res.json()["is_active"] is False

        # Non-existent
        res = await ac.put(
            "/admin/tenants/nonexistent-id", headers=h, json={"name": "X"}
        )
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_admin_rotate_key():
    """Cover admin.py L113-121."""
    h = await _admin_headers()
    transport = ASGITransport(app=admin_app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        get_res = await ac.get(f"/admin/tenants/{TEST_TENANT_ID}", headers=h)
        old_key = get_res.json()["api_key"]

        rot_res = await ac.post(
            f"/admin/tenants/{TEST_TENANT_ID}/rotate-key", headers=h
        )
        assert rot_res.status_code == 200
        assert rot_res.json()["api_key"] != old_key

        res = await ac.post("/admin/tenants/nonexistent-id/rotate-key", headers=h)
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_admin_delete_tenant():
    """Cover admin.py L103-110."""
    slug = _uniq("del")
    h = await _admin_headers()
    transport = ASGITransport(app=admin_app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        create_res = await ac.post(
            "/admin/tenants", headers=h, json={"name": "Del", "slug": slug}
        )
        tid = create_res.json()["id"]

        del_res = await ac.delete(f"/admin/tenants/{tid}", headers=h)
        assert del_res.status_code == 200
        assert del_res.json()["status"] == "success"

        res = await ac.get(f"/admin/tenants/{tid}", headers=h)
        assert res.status_code == 404

        res = await ac.delete("/admin/tenants/nonexistent-id", headers=h)
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_admin_management_config():
    """Cover admin.py L124-132."""
    h = await _admin_headers()
    transport = ASGITransport(app=admin_app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        res = await ac.get(
            f"/admin/tenants/{TEST_TENANT_ID}/management-config?class_identity=3-2",
            headers=h,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["IsManagementEnabled"] is True
        assert data["ClassIdentity"] == "3-2"
        assert TEST_TENANT_SLUG in data["ManagementServer"]


# ===========================================================================
# Auth middleware — auth.py (token-based)
# ===========================================================================


@pytest.mark.asyncio
async def test_auth_middleware_no_bearer_token():
    """Admin routes without Bearer token return 401."""
    transport = ASGITransport(app=admin_app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        res = await ac.get("/admin/tenants")
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_auth_middleware_invalid_bearer_token():
    """Admin routes with invalid Bearer token return 403."""
    transport = ASGITransport(app=admin_app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        res = await ac.get(
            "/admin/tenants", headers={"Authorization": "Bearer invalid"}
        )
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_auth_middleware_command_scope_on_admin():
    """Command-scoped token rejected on admin routes."""
    cmd_h = await _command_headers()
    transport = ASGITransport(app=admin_app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        res = await ac.get("/admin/tenants", headers=cmd_h)
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_auth_middleware_no_tenant_subdomain():
    """Cover auth.py: no tenant in hostname."""
    transport = ASGITransport(app=client_app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        res = await ac.get("/api/v1/client/test-uid/manifest")
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_auth_middleware_invalid_tenant_slug():
    """Cover auth.py: invalid tenant slug."""
    transport = ASGITransport(app=client_app)
    async with AsyncClient(
        transport=transport, base_url="http://nonexistent.localhost"
    ) as ac:
        res = await ac.get("/api/v1/client/test-uid/manifest")
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_auth_middleware_valid_tenant():
    """Cover auth.py: valid tenant from subdomain."""
    transport = ASGITransport(app=client_app)
    async with AsyncClient(
        transport=transport, base_url="http://test-school.localhost"
    ) as ac:
        res = await ac.get("/api/v1/client/test-uid/manifest")
        assert res.status_code == 200


# ===========================================================================
# gRPC Interceptor — auth.py
# ===========================================================================


@pytest.mark.asyncio
async def test_grpc_tenant_interceptor_with_authority():
    """Cover auth.py: TenantInterceptor extracting slug from :authority."""
    from app.core.auth import TenantInterceptor
    from unittest.mock import AsyncMock, MagicMock

    interceptor = TenantInterceptor()

    handler_call_details = MagicMock()
    handler_call_details.invocation_metadata = [
        (":authority", f"{TEST_TENANT_SLUG}.localhost:50052"),
    ]

    continuation = AsyncMock(return_value="handler")
    result = await interceptor.intercept_service(continuation, handler_call_details)
    assert result == "handler"
    continuation.assert_called_once()


@pytest.mark.asyncio
async def test_grpc_tenant_interceptor_with_tenant_id_metadata():
    """Cover auth.py: fallback to tenant-id metadata."""
    from app.core.auth import TenantInterceptor
    from unittest.mock import AsyncMock, MagicMock

    interceptor = TenantInterceptor()

    handler_call_details = MagicMock()
    handler_call_details.invocation_metadata = [
        ("tenant-id", TEST_TENANT_SLUG),
    ]

    continuation = AsyncMock(return_value="handler")
    result = await interceptor.intercept_service(continuation, handler_call_details)
    assert result == "handler"


@pytest.mark.asyncio
async def test_grpc_tenant_interceptor_no_tenant():
    """Cover auth.py: slug not None but tenant not found."""
    from app.core.auth import TenantInterceptor
    from unittest.mock import AsyncMock, MagicMock

    interceptor = TenantInterceptor()

    handler_call_details = MagicMock()
    handler_call_details.invocation_metadata = [
        (":authority", "unknown-tenant.localhost:50052"),
    ]

    continuation = AsyncMock(return_value="handler")
    result = await interceptor.intercept_service(continuation, handler_call_details)
    assert result == "handler"


@pytest.mark.asyncio
async def test_grpc_tenant_interceptor_no_metadata():
    """Cover auth.py: slug is None, no tenant-id fallback."""
    from app.core.auth import TenantInterceptor
    from unittest.mock import AsyncMock, MagicMock

    interceptor = TenantInterceptor()

    handler_call_details = MagicMock()
    handler_call_details.invocation_metadata = []

    continuation = AsyncMock(return_value="handler")
    result = await interceptor.intercept_service(continuation, handler_call_details)
    assert result == "handler"


# ===========================================================================
# Tenant resolution — tenant.py
# ===========================================================================


def test_extract_slug_from_host_cases():
    """Cover tenant.py L46-53."""
    assert extract_slug_from_host("school-a.localhost:50050") == "school-a"
    assert extract_slug_from_host("localhost:50050") is None
    assert extract_slug_from_host("localhost") is None
    assert extract_slug_from_host("") is None


def test_get_tenant_id_no_context():
    """Cover tenant.py L32-33: tenant_ctx not set."""
    import contextvars

    def _run():
        try:
            get_tenant_id()
            return False
        except RuntimeError:
            return True

    from app.core.tenant import tenant_ctx as tctx

    token = tctx.set("temp")
    tctx.reset(token)
    new_ctx = contextvars.Context()
    assert new_ctx.run(_run) is True


@pytest.mark.asyncio
async def test_resolve_tenant_cached():
    """Cover tenant.py: cache hit path."""
    import json

    rd = get_redis()
    await rd.set(
        f"tenant:{TEST_TENANT_SLUG}",
        json.dumps(
            {
                "id": TEST_TENANT_ID,
                "name": "Cached",
                "slug": TEST_TENANT_SLUG,
                "api_key": "cached-key",
                "is_active": True,
            }
        ),
        ex=60,
    )
    async with AsyncSessionLocal() as db:
        result = await resolve_tenant(TEST_TENANT_SLUG, db)
    assert result is not None
    assert result.id == TEST_TENANT_ID
    await rd.delete(f"tenant:{TEST_TENANT_SLUG}")


@pytest.mark.asyncio
async def test_resolve_tenant_cached_inactive():
    """Cover tenant.py: cached but inactive tenant."""
    import json

    rd = get_redis()
    await rd.set(
        "tenant:inactive-cached",
        json.dumps(
            {
                "id": "x",
                "name": "X",
                "slug": "inactive-cached",
                "api_key": "x",
                "is_active": False,
            }
        ),
        ex=60,
    )
    async with AsyncSessionLocal() as db:
        result = await resolve_tenant("inactive-cached", db)
    assert result is None
    await rd.delete("tenant:inactive-cached")


@pytest.mark.asyncio
async def test_resolve_tenant_db_miss():
    """Cover tenant.py: DB miss."""
    rd = get_redis()
    await rd.delete("tenant:totally-unknown")
    async with AsyncSessionLocal() as db:
        result = await resolve_tenant("totally-unknown", db)
    assert result is None


@pytest.mark.asyncio
async def test_resolve_tenant_db_inactive():
    """Cover tenant.py: found in DB but inactive."""
    from datetime import datetime, timezone

    slug = _uniq("inactive")
    async with AsyncSessionLocal() as db:
        db.add(
            Tenant(
                id=_uniq("tid"),
                name="Inactive",
                slug=slug,
                api_key="x",
                is_active=False,
                created_at=datetime.now(timezone.utc),
            )
        )
        await db.commit()

    rd = get_redis()
    await rd.delete(f"tenant:{slug}")

    async with AsyncSessionLocal() as db:
        result = await resolve_tenant(slug, db)
    assert result is None


@pytest.mark.asyncio
async def test_resolve_tenant_cache_miss_populates():
    """Cover tenant.py: cache miss populates cache."""
    rd = get_redis()
    await rd.delete(f"tenant:{TEST_TENANT_SLUG}")
    async with AsyncSessionLocal() as db:
        result = await resolve_tenant(TEST_TENANT_SLUG, db)
    assert result is not None
    assert result.id == TEST_TENANT_ID
    cached = await rd.get(f"tenant:{TEST_TENANT_SLUG}")
    assert cached is not None


# ===========================================================================
# Management config endpoint — management_config.py
# ===========================================================================


@pytest.mark.asyncio
async def test_management_config_via_subdomain():
    """Cover management_config.py full path."""
    transport = ASGITransport(app=client_app)
    async with AsyncClient(
        transport=transport, base_url="http://test-school.localhost"
    ) as ac:
        res = await ac.get("/api/v1/management-config?class_identity=1-1")
    assert res.status_code == 200
    data = res.json()
    assert data["IsManagementEnabled"] is True
    assert data["ClassIdentity"] == "1-1"
    assert "test-school" in data["ManagementServer"]


# ===========================================================================
# gRPC server.py — _get_tenant_id_safe fallback
# ===========================================================================


def test_get_tenant_id_safe_no_context():
    """Cover server.py: _get_tenant_id_safe fallback."""
    from app.grpc.server import _get_tenant_id_safe
    import contextvars

    new_ctx = contextvars.Context()
    result = new_ctx.run(_get_tenant_id_safe)
    assert result == ""


# ===========================================================================
# gRPC server.py — ListenCommand tenant fallback from session
# ===========================================================================


@pytest.mark.asyncio
async def test_listen_command_tenant_from_session():
    """Cover server.py: tenant_id from session when no interceptor context."""
    import asyncio
    from app.grpc.server import ClientCommandDeliverServicer
    from app.grpc.session_manager import SessionManager
    from app.grpc.api.Protobuf.Client import ClientCommandDeliverScReq_pb2
    from app.grpc.api.Protobuf.Enum import CommandTypes_pb2
    from unittest.mock import MagicMock, AsyncMock, patch

    sm = SessionManager()
    await sm.store_pending_handshake(TEST_TENANT_ID, "tent-uid", "token")
    sid = await sm.complete_handshake(TEST_TENANT_ID, "tent-uid", accepted=True)
    assert sid is not None

    servicer = ClientCommandDeliverServicer(sm)
    ctx = MagicMock()
    ctx.invocation_metadata.return_value = [("cuid", "tent-uid"), ("session", sid)]
    ctx.peer.return_value = "ipv4:127.0.0.1:5555"
    ctx.abort = AsyncMock()

    async def req_iterator():
        yield ClientCommandDeliverScReq_pb2.ClientCommandDeliverScReq(
            Type=CommandTypes_pb2.Ping
        )
        await asyncio.sleep(0.1)

    with patch("app.grpc.server._get_tenant_id_safe", return_value=""):
        gen = servicer.ListenCommand(req_iterator(), ctx)
        iterator = gen.__aiter__()
        rsp = await asyncio.wait_for(iterator.__anext__(), timeout=2.0)
        assert rsp is not None


# ===========================================================================
# Session manager — empty session_id short-circuit
# ===========================================================================


@pytest.mark.asyncio
async def test_validate_session_empty_id():
    """Cover session_manager.py: empty session_id."""
    from app.grpc.session_manager import SessionManager

    sm = SessionManager()
    assert await sm.validate_session("") is None


@pytest.mark.asyncio
async def test_get_session_tenant_empty_id():
    """Cover session_manager.py: empty session_id."""
    from app.grpc.session_manager import SessionManager

    sm = SessionManager()
    assert await sm.get_session_tenant("") is None


# ===========================================================================
# Resource token — multi-use token
# ===========================================================================


@pytest.mark.asyncio
async def test_multi_use_token():
    """Cover resource_token.py: token with multiple uses."""
    from app.services.resource_token import create_token, resolve_token

    token = await create_token(TEST_TENANT_ID, "ClassPlan", "multi_res", max_uses=3)
    assert token

    r1 = await resolve_token(token)
    assert r1 is not None

    r2 = await resolve_token(token)
    assert r2 is not None

    r3 = await resolve_token(token)
    assert r3 is not None

    r4 = await resolve_token(token)
    assert r4 is None


# ===========================================================================
# Client API redirect — client.py
# ===========================================================================


@pytest.mark.asyncio
async def test_client_resource_redirect_via_middleware():
    """Cover client.py redirect."""
    cmd_h = await _command_headers()
    admin_transport = ASGITransport(app=admin_app)
    async with AsyncClient(
        transport=admin_transport, base_url="http://test-school.localhost"
    ) as ac:
        await ac.get(
            "/command/datas/ClassPlan/create?name=redir_test_cov", headers=cmd_h
        )
        await ac.put(
            "/command/datas/ClassPlan/write?name=redir_test_cov",
            json={"r": True},
            headers=cmd_h,
        )

    client_transport = ASGITransport(app=client_app)
    async with AsyncClient(
        transport=client_transport, base_url="http://test-school.localhost"
    ) as cc:
        res = await cc.get(
            "/api/v1/client/ClassPlan?name=redir_test_cov", follow_redirects=False
        )
        assert res.status_code == 302
        assert "/get?token=" in res.headers["location"]


# ===========================================================================
# Redis stale pool
# ===========================================================================


@pytest.mark.asyncio
async def test_redis_init_resilient():
    """Cover redis.py init_redis re-init path."""
    from app.core.redis import init_redis

    pool = await init_redis()
    assert pool is not None
    await pool.ping()


@pytest.mark.asyncio
async def test_redis_stale_pool_aclose_exception():
    """Cover redis.py: stale pool where aclose() raises."""
    import app.core.redis as redis_mod
    from unittest.mock import AsyncMock, MagicMock

    fake_pool = MagicMock()
    fake_pool.ping = AsyncMock(side_effect=RuntimeError("wrong loop"))
    fake_pool.aclose = AsyncMock(side_effect=OSError("already closed"))

    original_pool = redis_mod._pool
    redis_mod._pool = fake_pool

    try:
        pool = await redis_mod.init_redis()
        assert pool is not None
        await pool.ping()
    finally:
        redis_mod._pool = original_pool


@pytest.mark.asyncio
async def test_get_redis_not_initialized():
    """Cover redis.py: get_redis when pool is None."""
    import app.core.redis as redis_mod

    original_pool = redis_mod._pool
    redis_mod._pool = None
    try:
        with pytest.raises(RuntimeError, match="Redis pool not initialised"):
            redis_mod.get_redis()
    finally:
        redis_mod._pool = original_pool


# ===========================================================================
# server.py: invalid session warning + non-Ping command
# ===========================================================================


@pytest.mark.asyncio
async def test_listen_command_invalid_session_warning():
    """Cover server.py: session provided but invalid → warning."""
    import asyncio
    from app.grpc.server import ClientCommandDeliverServicer
    from app.grpc.session_manager import SessionManager
    from app.grpc.api.Protobuf.Client import ClientCommandDeliverScReq_pb2
    from app.grpc.api.Protobuf.Enum import CommandTypes_pb2
    from unittest.mock import MagicMock, AsyncMock

    sm = SessionManager()
    servicer = ClientCommandDeliverServicer(sm)

    ctx = MagicMock()
    ctx.invocation_metadata.return_value = [
        ("cuid", "inv-session-uid"),
        ("session", "invalid-session-id-that-does-not-exist"),
    ]
    ctx.peer.return_value = "ipv4:127.0.0.1:7777"
    ctx.abort = AsyncMock()

    async def req_iterator():
        yield ClientCommandDeliverScReq_pb2.ClientCommandDeliverScReq(
            Type=CommandTypes_pb2.Ping
        )
        await asyncio.sleep(0.1)

    gen = servicer.ListenCommand(req_iterator(), ctx)
    iterator = gen.__aiter__()
    rsp = await asyncio.wait_for(iterator.__anext__(), timeout=2.0)
    assert rsp.Type == CommandTypes_pb2.Pong


@pytest.mark.asyncio
async def test_listen_command_non_ping_command():
    """Cover server.py: non-Ping command type → logger.info."""
    import asyncio
    from app.grpc.server import ClientCommandDeliverServicer
    from app.grpc.session_manager import SessionManager
    from app.grpc.api.Protobuf.Client import ClientCommandDeliverScReq_pb2
    from app.grpc.api.Protobuf.Enum import CommandTypes_pb2
    from unittest.mock import MagicMock, AsyncMock

    sm = SessionManager()
    servicer = ClientCommandDeliverServicer(sm)

    ctx = MagicMock()
    ctx.invocation_metadata.return_value = [
        ("cuid", "nonping-uid"),
        ("session", ""),
    ]
    ctx.peer.return_value = "ipv4:127.0.0.1:6666"
    ctx.abort = AsyncMock()

    async def req_iterator():
        yield ClientCommandDeliverScReq_pb2.ClientCommandDeliverScReq(
            Type=CommandTypes_pb2.RestartApp
        )
        await asyncio.sleep(0.2)

    gen = servicer.ListenCommand(req_iterator(), ctx)
    iterator = gen.__aiter__()

    try:
        await asyncio.wait_for(iterator.__anext__(), timeout=0.5)
    except (asyncio.TimeoutError, StopAsyncIteration):
        pass  # Expected — non-Ping doesn't produce a response


# ===========================================================================
# Auth token service — lifecycle tests
# ===========================================================================


@pytest.mark.asyncio
async def test_auth_token_lifecycle():
    """Test token generation, validation, refresh, and revocation."""
    from app.services.auth_token import (
        generate_token,
        validate_and_refresh,
        revoke_token,
    )

    # Generate
    token = await generate_token("admin")
    assert token

    # Validate
    result = await validate_and_refresh(token)
    assert result == ("admin", "")

    # Validate with tenant
    cmd_token = await generate_token("command", tenant_id=TEST_TENANT_ID)
    result = await validate_and_refresh(cmd_token)
    assert result == ("command", TEST_TENANT_ID)

    # Revoke
    assert await revoke_token(token) is True
    assert await validate_and_refresh(token) is None

    # Revoke non-existent
    assert await revoke_token("nonexistent") is False

    # Validate empty
    assert await validate_and_refresh("") is None
    assert await revoke_token("") is False


@pytest.mark.asyncio
async def test_auth_token_expiry():
    """Test that tokens expire after TTL."""
    import asyncio
    from app.services.auth_token import generate_token, validate_and_refresh

    token = await generate_token("admin", ttl=1)
    # Verify token exists via Redis directly (don't validate which refreshes TTL)
    from app.core.redis import get_redis

    rd = get_redis()
    assert await rd.exists(f"auth:{token}")

    await asyncio.sleep(2.0)
    assert await validate_and_refresh(token) is None


@pytest.mark.asyncio
async def test_admin_create_command_token():
    """Test POST /admin/tenants/{id}/auth/token generates command token."""
    h = await _admin_headers()
    transport = ASGITransport(app=admin_app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        res = await ac.post(f"/admin/tenants/{TEST_TENANT_ID}/auth/token", headers=h)
        assert res.status_code == 200
        data = res.json()
        assert "token" in data
        assert data["token_type"] == "Bearer"

        # Use the token on command endpoint
        cmd_h = {"Authorization": f"Bearer {data['token']}"}
        cmd_transport = ASGITransport(app=admin_app)
        async with AsyncClient(
            transport=cmd_transport, base_url="http://test-school.localhost"
        ) as cc:
            res = await cc.get("/command/clients/list", headers=cmd_h)
            assert res.status_code == 200

        # Non-existent tenant
        res = await ac.post("/admin/tenants/nonexistent-id/auth/token", headers=h)
        assert res.status_code == 404

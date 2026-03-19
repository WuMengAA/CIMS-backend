"""Shared test fixtures — sets up PG, Redis, and a default test tenant."""

import os
from datetime import datetime, timezone

import pytest_asyncio

# Force test key file location before any imports that read the env
os.environ.setdefault("CIMS_KEY_FILE", "/tmp/test_cims_server.key")

from app.core.redis import init_redis  # noqa: E402
from app.models.database import init_db, AsyncSessionLocal, Tenant  # noqa: E402
from app.core.tenant import tenant_ctx  # noqa: E402

TEST_TENANT_ID = "test-tenant-00000000"
TEST_TENANT_SLUG = "test-school"
TEST_TENANT_NAME = "Test School"


@pytest_asyncio.fixture(autouse=True)
async def setup_infra():
    """Init PG tables + Redis pool. Both are idempotent."""
    await init_redis()
    await init_db()
    yield


@pytest_asyncio.fixture(autouse=True)
async def test_tenant():
    """Ensure a test tenant exists and set the ContextVar for every test."""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select

        result = await db.execute(select(Tenant).where(Tenant.id == TEST_TENANT_ID))
        if result.scalar_one_or_none() is None:
            db.add(
                Tenant(
                    id=TEST_TENANT_ID,
                    name=TEST_TENANT_NAME,
                    slug=TEST_TENANT_SLUG,
                    api_key="test-api-key",
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                )
            )
            await db.commit()

    token = tenant_ctx.set(TEST_TENANT_ID)
    yield TEST_TENANT_ID
    tenant_ctx.reset(token)


@pytest_asyncio.fixture()
async def admin_token():
    """Generate an admin-scoped auth token for testing."""
    from app.services.auth_token import generate_token

    return await generate_token("admin")


@pytest_asyncio.fixture()
async def command_token():
    """Generate a command-scoped auth token for the test tenant."""
    from app.services.auth_token import generate_token

    return await generate_token("command", tenant_id=TEST_TENANT_ID)


@pytest_asyncio.fixture()
async def admin_headers(admin_token):
    """Convenience: Authorization headers for admin requests."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest_asyncio.fixture()
async def command_headers(command_token):
    """Convenience: Authorization headers for command requests."""
    return {"Authorization": f"Bearer {command_token}"}

"""限额边界与并发测试。

验证限额设置、边界条件、溢出保护和并发递增行为。
"""

import pytest
import pytest_asyncio
import uuid
from app.models.engine import AsyncSessionLocal
from app.services.quota.enforcer import increment_quota
from app.services.quota.manager import set_quota
from app.models.account_quota import AccountQuota
from sqlalchemy import delete

_ACCT = f"quota-edge-{uuid.uuid4().hex[:8]}"


@pytest_asyncio.fixture(autouse=True)
async def _cleanup():
    """测试后清理。"""
    yield
    async with AsyncSessionLocal() as db:
        await db.execute(delete(AccountQuota).where(AccountQuota.account_id == _ACCT))
        await db.commit()


@pytest.mark.asyncio
async def test_quota_exact_boundary():
    """在精确边界上的递增行为。"""
    async with AsyncSessionLocal() as db:
        q = await set_quota(_ACCT, "max_clients", 3, db)
        q.current_value = 2
        await db.commit()
        # 2 → 3 应成功（刚好到上限）
        assert await increment_quota(_ACCT, "max_clients", db)
        # 3 → 4 应失败
        assert not await increment_quota(_ACCT, "max_clients", db)


@pytest.mark.asyncio
async def test_quota_zero_limit():
    """限额为 0 时任何递增都应失败。"""
    async with AsyncSessionLocal() as db:
        await set_quota(_ACCT, "zero_test", 0, db)
        assert not await increment_quota(_ACCT, "zero_test", db)


@pytest.mark.asyncio
async def test_quota_large_increment():
    """大步长递增应正确计算。"""
    async with AsyncSessionLocal() as db:
        await set_quota(_ACCT, "bandwidth", 1000, db)
        assert await increment_quota(_ACCT, "bandwidth", db, amount=500)
        assert await increment_quota(_ACCT, "bandwidth", db, amount=500)
        # 已用完 1000，再加 1 应失败
        assert not await increment_quota(_ACCT, "bandwidth", db, amount=1)


@pytest.mark.asyncio
async def test_quota_unlimited_large_amount():
    """无限制（-1）时大数量递增始终成功。"""
    async with AsyncSessionLocal() as db:
        await set_quota(_ACCT, "unlimited", -1, db)
        assert await increment_quota(_ACCT, "unlimited", db, amount=999999999)


@pytest.mark.asyncio
async def test_quota_update_limit():
    """修改限额上限后应立即生效。"""
    async with AsyncSessionLocal() as db:
        q = await set_quota(_ACCT, "dynamic", 5, db)
        q.current_value = 5
        await db.commit()
        # 已满
        assert not await increment_quota(_ACCT, "dynamic", db)
        # 提高上限
        await set_quota(_ACCT, "dynamic", 10, db)
        assert await increment_quota(_ACCT, "dynamic", db)


@pytest.mark.asyncio
async def test_multiple_quota_keys():
    """多个限额键互不影响。"""
    async with AsyncSessionLocal() as db:
        await set_quota(_ACCT, "key_a", 1, db)
        await set_quota(_ACCT, "key_b", 100, db)
        assert await increment_quota(_ACCT, "key_a", db)
        assert not await increment_quota(_ACCT, "key_a", db)
        # key_b 不受影响
        assert await increment_quota(_ACCT, "key_b", db)

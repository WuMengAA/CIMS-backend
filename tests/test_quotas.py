"""限额管理与执行测试。

测试限额设置、递增消耗、超限拒绝和无限制场景。
"""

import uuid
import pytest
import pytest_asyncio

from app.models.engine import AsyncSessionLocal
from app.services.quota.enforcer import check_quota, increment_quota
from app.services.quota.manager import set_quota, get_quotas
from app.models.account_quota import AccountQuota
from sqlalchemy import delete

_TEST_ACCT = f"quota-test-{uuid.uuid4().hex[:8]}"


@pytest_asyncio.fixture(autouse=True)
async def _cleanup_quotas():
    """测试后清理配额数据。"""
    yield
    async with AsyncSessionLocal() as db:
        await db.execute(
            delete(AccountQuota).where(AccountQuota.account_id == _TEST_ACCT)
        )
        await db.commit()


@pytest.mark.asyncio
async def test_set_and_get_quota():
    """设置限额后应能正确查询。"""
    async with AsyncSessionLocal() as db:
        await set_quota(_TEST_ACCT, "max_clients", 10, db)
        quotas = await get_quotas(_TEST_ACCT, db)
        assert len(quotas) == 1
        assert quotas[0].max_value == 10


@pytest.mark.asyncio
async def test_increment_within_limit():
    """在限额内递增应成功。"""
    async with AsyncSessionLocal() as db:
        await set_quota(_TEST_ACCT, "max_clients", 5, db)
        result = await increment_quota(_TEST_ACCT, "max_clients", db)
        assert result is True


@pytest.mark.asyncio
async def test_increment_exceeds_limit():
    """超限时递增应失败。"""
    async with AsyncSessionLocal() as db:
        q = await set_quota(_TEST_ACCT, "max_clients", 2, db)
        q.current_value = 2
        await db.commit()
        result = await increment_quota(_TEST_ACCT, "max_clients", db)
        assert result is False


@pytest.mark.asyncio
async def test_unlimited_quota():
    """-1 表示无限制，始终允许。"""
    async with AsyncSessionLocal() as db:
        await set_quota(_TEST_ACCT, "bandwidth", -1, db)
        assert await check_quota(_TEST_ACCT, "bandwidth", db) is True
        assert await increment_quota(_TEST_ACCT, "bandwidth", db, amount=999999) is True


@pytest.mark.asyncio
async def test_unconfigured_quota_passes():
    """未配置的限额键应视为允许。"""
    async with AsyncSessionLocal() as db:
        assert await check_quota(_TEST_ACCT, "nonexistent_key", db) is True

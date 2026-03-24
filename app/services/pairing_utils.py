"""配对码生成与验证工具。

提供配对码的生成、校验和消费功能。
"""

import secrets
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app.models.database import AsyncSessionLocal
from app.models.pairing import PairingCode
from app.core.tenant.context import set_search_path

logger = logging.getLogger(__name__)

# 易辨识字符集（排除 0/O/1/I/D/Q/U/V 等易混淆字符）
_CHARSET = "2346789ABCEFGHJKLMNPRSTWXYZ"
_CODE_LEN = 8


def generate_code() -> str:
    """随机生成一个 8 位配对码。"""
    return "".join(secrets.choice(_CHARSET) for _ in range(_CODE_LEN))


async def create_pairing_request(
    tenant_id: str,
    client_uid: str,
    client_id: str = "",
    client_mac: str = "",
    client_ip: str = "",
) -> str:
    """创建配对请求并返回配对码。"""
    code = generate_code()
    record = PairingCode(
        code=code,
        tenant_id=tenant_id,
        client_uid=client_uid,
        client_id=client_id,
        client_mac=client_mac,
        client_ip=client_ip,
        created_at=datetime.now(timezone.utc),
    )
    async with AsyncSessionLocal() as db:
        await set_search_path(db)
        db.add(record)
        await db.commit()
    logger.info("生成配对码 %s（租户=%s, 设备=%s）", code, tenant_id, client_uid)
    return code


async def check_approved(client_uid: str, tenant_id: str) -> bool:
    """检查设备是否有已审批的配对码。"""
    async with AsyncSessionLocal() as db:
        await set_search_path(db)
        stmt = (
            select(PairingCode)
            .where(PairingCode.client_uid == client_uid)
            .where(PairingCode.tenant_id == tenant_id)
            .where(PairingCode.approved.is_(True))
            .where(PairingCode.used.is_(False))
        )
        record = (await db.execute(stmt)).scalar_one_or_none()
        if record:
            record.used = True
            await db.commit()
            return True
    return False


async def get_pairing_by_code(code: str, tenant_id: str):
    """根据配对码查询详情（供管理员查看）。"""
    async with AsyncSessionLocal() as db:
        await set_search_path(db)
        stmt = (
            select(PairingCode)
            .where(PairingCode.code == code)
            .where(PairingCode.tenant_id == tenant_id)
        )
        return (await db.execute(stmt)).scalar_one_or_none()


async def approve_pairing(code: str, tenant_id: str) -> bool:
    """审批配对码。"""
    async with AsyncSessionLocal() as db:
        await set_search_path(db)
        stmt = (
            select(PairingCode)
            .where(PairingCode.code == code)
            .where(PairingCode.tenant_id == tenant_id)
        )
        record = (await db.execute(stmt)).scalar_one_or_none()
        if not record or record.used:
            return False
        record.approved = True
        await db.commit()
        logger.info("审批配对码 %s（租户=%s）", code, tenant_id)
        return True


async def revoke_pairing(code: str, tenant_id: str) -> bool:
    """撤销配对码。"""
    async with AsyncSessionLocal() as db:
        await set_search_path(db)
        from sqlalchemy import delete as sa_delete

        result = await db.execute(
            sa_delete(PairingCode)
            .where(PairingCode.code == code)
            .where(PairingCode.tenant_id == tenant_id)
        )
        await db.commit()
        return result.rowcount > 0  # type: ignore[union-attr]


async def list_pending(tenant_id: str) -> list:
    """列出指定租户的待审批配对码。"""
    async with AsyncSessionLocal() as db:
        await set_search_path(db)
        stmt = (
            select(PairingCode)
            .where(PairingCode.tenant_id == tenant_id)
            .where(PairingCode.used.is_(False))
            .order_by(PairingCode.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

"""客户端清单（Manifest）生成。

为终端设备提供获取其动态配置集（课表等）的接口。
"""

import time
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenant.context import get_tenant_id
from app.models.database import get_db, ClientProfile
from app.api.schemas.client import ClientManifest

router = APIRouter()


@router.get("/v1/client/{client_uid}/manifest", response_model=ClientManifest)
async def get_client_manifest(client_uid: str, db: AsyncSession = Depends(get_db)):
    """为请求的 UID 构建完整的 Manifest JSON 数据。"""
    tenant_id = get_tenant_id()
    stmt = select(ClientProfile).where(
        ClientProfile.tenant_id == tenant_id, ClientProfile.client_id == client_uid
    )
    result = await db.execute(stmt)
    p = result.scalar_one_or_none() or ClientProfile()

    # Apply defaults if profile incomplete
    cp = p.class_plan or "default_classplan"
    tl = p.time_layout or "default_timelayout"
    cur = int(time.time())

    return ClientManifest(
        ClassPlanSource={
            "Value": f"/api/v1/client/ClassPlan?name={cp}",
            "Version": cur,
        },
        TimeLayoutSource={
            "Value": f"/api/v1/client/TimeLayout?name={tl}",
            "Version": cur,
        },
        SubjectsSource={
            "Value": "/api/v1/client/Subjects?name=default",
            "Version": cur,
        },
        DefaultSettingsSource={
            "Value": "/api/v1/client/DefaultSettings?name=default",
            "Version": cur,
        },
        PolicySource={"Value": "/api/v1/client/Policy?name=default", "Version": cur},
        ComponentsSource={
            "Value": "/api/v1/client/Components?name=default",
            "Version": cur,
        },
        CredentialSource={
            "Value": "/api/v1/client/Credentials?name=default",
            "Version": cur,
        },
        CoreVersion={"Major": 1, "Minor": 4, "Build": 0, "Revision": 0},
    )

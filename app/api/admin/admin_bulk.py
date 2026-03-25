"""超管批量操作路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.command.batch import process_batch
from app.api.schemas.batch import BatchRequest
from app.models.database import get_db

router = APIRouter()


@router.post("")
async def admin_bulk(
    req: BatchRequest,
    db: AsyncSession = Depends(get_db),
):
    """以超管身份执行批量操作。"""
    return await process_batch(req, db)

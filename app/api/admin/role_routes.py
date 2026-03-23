"""角色分级管理路由。

提供角色列表查询、创建和删除端点，
需要超级管理员权限。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import get_db
from app.core.auth.dependencies import require_role
from app.api.schemas.role import RoleCreateRequest, RoleOut
from app.services.user.role_manager import (
    list_roles,
    create_role,
    delete_role,
)

router = APIRouter()
_superadmin = require_role(100)


@router.get("", response_model=list[RoleOut])
async def list_all_roles(
    db: AsyncSession = Depends(get_db),
    _user=Depends(_superadmin),
):
    """查询所有角色分级（需超级管理员）。"""
    roles = await list_roles(db)
    return [_to_out(r) for r in roles]


@router.post("", response_model=RoleOut)
async def create_new_role(
    body: RoleCreateRequest,
    db: AsyncSession = Depends(get_db),
    _user=Depends(_superadmin),
):
    """创建自定义角色（需超级管理员）。"""
    role = await create_role(body.code, body.label, body.priority, db)
    return _to_out(role)


@router.delete("/{code}")
async def delete_existing_role(
    code: str,
    db: AsyncSession = Depends(get_db),
    _user=Depends(_superadmin),
):
    """删除自定义角色（系统内置不可删）。"""
    err = await delete_role(code, db)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return {"status": "success", "message": f"角色 {code} 已删除"}


def _to_out(role) -> RoleOut:
    """将 CustomRole 模型转换为响应模型。"""
    return RoleOut(
        id=role.id,
        code=role.code,
        label=role.label,
        priority=role.priority,
        is_system=role.is_system,
    )

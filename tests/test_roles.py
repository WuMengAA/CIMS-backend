"""角色分级管理测试。

测试系统角色初始化、自定义角色 CRUD 和系统角色保护。
"""

import pytest

from app.models.engine import AsyncSessionLocal
from app.services.user.role_manager import (
    ensure_system_roles,
    list_roles,
    create_role,
    delete_role,
    SYSTEM_ROLES,
)


@pytest.mark.asyncio
async def test_ensure_system_roles():
    """系统角色应正确初始化。"""
    async with AsyncSessionLocal() as db:
        await ensure_system_roles(db)
        roles = await list_roles(db)
        codes = {r.code for r in roles}
        for code, _, _ in SYSTEM_ROLES:
            assert code in codes


@pytest.mark.asyncio
async def test_system_roles_are_protected():
    """系统内置角色不可删除。"""
    async with AsyncSessionLocal() as db:
        await ensure_system_roles(db)
        err = await delete_role("superadmin", db)
        assert err == "系统内置角色不可删除"


@pytest.mark.asyncio
async def test_create_custom_role():
    """创建自定义角色应成功。"""
    async with AsyncSessionLocal() as db:
        role = await create_role("teacher", "教师", 50, db)
        assert role.code == "teacher"
        assert role.is_system is False
        assert role.priority == 50
        # 清理
        await delete_role("teacher", db)


@pytest.mark.asyncio
async def test_delete_custom_role():
    """删除自定义角色应成功。"""
    async with AsyncSessionLocal() as db:
        await create_role("temp_role", "临时角色", 5, db)
        err = await delete_role("temp_role", db)
        assert err is None


@pytest.mark.asyncio
async def test_delete_nonexistent_role():
    """删除不存在的角色应返回错误。"""
    async with AsyncSessionLocal() as db:
        err = await delete_role("nonexistent_xyz", db)
        assert err == "角色不存在"


@pytest.mark.asyncio
async def test_roles_sorted_by_priority():
    """角色列表应按优先级降序排列。"""
    async with AsyncSessionLocal() as db:
        await ensure_system_roles(db)
        roles = await list_roles(db)
        priorities = [r.priority for r in roles]
        assert priorities == sorted(priorities, reverse=True)

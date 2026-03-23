"""用户认证与注册测试。

测试注册流程、自动创建账户、登录验证、令牌管理和角色检查。
"""

import pytest
import pytest_asyncio
from app.models.engine import AsyncSessionLocal
from app.services.user.register import register_user
from app.services.user.login import login_user
from app.services.crypto.hasher import hash_password, verify_password
from sqlalchemy import select, delete
from app.models.user import User
from app.models.account import Account
from app.models.account_member import AccountMember


@pytest_asyncio.fixture(autouse=True)
async def _cleanup_test_users():
    """测试后清理注册的用户。"""
    yield
    async with AsyncSessionLocal() as db:
        await db.execute(
            delete(AccountMember).where(
                AccountMember.user_id.in_(
                    select(User.id).where(User.email.like("%@regtest.com"))
                )
            )
        )
        await db.execute(delete(Account).where(Account.slug.like("reg_%")))
        await db.execute(delete(User).where(User.email.like("%@regtest.com")))
        await db.commit()


@pytest.mark.asyncio
async def test_register_creates_user_and_account():
    """注册 → 用户和账户同时创建。"""
    async with AsyncSessionLocal() as db:
        user = await register_user(
            "reg_test_user",
            "reg@regtest.com",
            "StrongPass123!",
            "测试用户",
            db,
        )
        assert user.username == "reg_test_user"
        assert user.role_code == "normal"
        # 验证账户已创建
        result = await db.execute(
            select(Account).where(Account.slug == "reg-test-user")
        )
        account = result.scalar_one_or_none()
        assert account is not None
        # 验证成员关系
        result = await db.execute(
            select(AccountMember).where(AccountMember.user_id == user.id)
        )
        member = result.scalar_one_or_none()
        assert member is not None
        assert member.role_in_account == "owner"


@pytest.mark.asyncio
async def test_register_rejects_invalid_username():
    """用户名格式不合法应被拒绝。"""
    async with AsyncSessionLocal() as db:
        with pytest.raises(ValueError, match="格式"):
            await register_user(
                "AB",
                "bad@regtest.com",
                "StrongPass123!",
                "",
                db,
            )


@pytest.mark.asyncio
async def test_register_rejects_duplicate():
    """重复用户名或邮箱应被拒绝。"""
    async with AsyncSessionLocal() as db:
        await register_user(
            "reg_dup_user",
            "dup@regtest.com",
            "StrongPass123!",
            "",
            db,
        )
        with pytest.raises(ValueError, match="已被注册"):
            await register_user(
                "reg_dup_user",
                "dup2@regtest.com",
                "StrongPass123!",
                "",
                db,
            )


@pytest.mark.asyncio
async def test_login_success():
    """有效凭据应登录成功并返回令牌。"""
    async with AsyncSessionLocal() as db:
        await register_user(
            "reg_login_user",
            "login@regtest.com",
            "StrongPass123!",
            "",
            db,
        )
        token, user, needs_2fa = await login_user("login@regtest.com", "StrongPass123!", db)
        assert token
        assert not needs_2fa
        assert user.username == "reg_login_user"


@pytest.mark.asyncio
async def test_login_wrong_password():
    """错误密码应被拒绝。"""
    async with AsyncSessionLocal() as db:
        await register_user(
            "reg_wrongpw",
            "wrongpw@regtest.com",
            "StrongPass123!",
            "",
            db,
        )
        with pytest.raises(ValueError, match="错误"):
            await login_user("wrongpw@regtest.com", "WrongPass!", db)


@pytest.mark.asyncio
async def test_login_banned_user():
    """已封禁用户不允许登录。"""
    async with AsyncSessionLocal() as db:
        user = await register_user(
            "reg_banned",
            "banned@regtest.com",
            "StrongPass123!",
            "",
            db,
        )
        user.role_code = "banned"
        await db.commit()
        with pytest.raises(ValueError, match="封禁"):
            await login_user("banned@regtest.com", "StrongPass123!", db)


@pytest.mark.asyncio
async def test_argon2id_hash_and_verify():
    """Argon2id 哈希与验证功能测试。"""
    hashed = hash_password("TestPassword123!")
    assert hashed.startswith("$argon2id$")
    assert verify_password("TestPassword123!", hashed)
    assert not verify_password("WrongPassword!", hashed)

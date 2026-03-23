"""account 子命令处理器。

支持 list / create / delete / add-member / remove-member 操作。
"""

import asyncio
import uuid
import secrets
from datetime import datetime, timezone
from sqlalchemy import select


def handle_account(args) -> None:
    """分发账户管理操作。"""
    act = getattr(args, "account_action", None)
    if not act:
        print("请指定操作: list/create/delete/add-member/remove-member")
        return
    asyncio.run(_dispatch(act, args))


async def _dispatch(act, args) -> None:
    """异步分发账户操作。"""
    from app.models.engine import AsyncSessionLocal
    from app.models.account import Account

    async with AsyncSessionLocal() as db:
        if act == "list":
            r = await db.execute(select(Account))
            for a in r.scalars().all():
                print(f"  {a.slug} ({a.name}) [active={a.is_active}]")
        elif act == "create":
            await _create_account(args, db)
        elif act == "delete":
            await _delete_account(args, db)
        elif act == "add-member":
            await _add_member(args, db)
        elif act == "remove-member":
            await _remove_member(args, db)


async def _create_account(args, db) -> None:
    """创建新账户。"""
    from app.models.account import Account

    db.add(
        Account(
            id=str(uuid.uuid4()),
            name=args.name,
            slug=args.slug,
            api_key=secrets.token_urlsafe(32),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
    )
    await db.commit()
    print(f"✅ 账户 {args.slug} 已创建")


async def _delete_account(args, db) -> None:
    """删除账户。"""
    from app.models.account import Account

    acct = (
        await db.execute(select(Account).where(Account.slug == args.slug))
    ).scalar_one_or_none()
    if not acct:
        print(f"❌ 账户 {args.slug} 不存在")
        return
    await db.delete(acct)
    await db.commit()
    print(f"✅ 账户 {args.slug} 已删除")


async def _add_member(args, db) -> None:
    """向账户添加成员。"""
    from app.models.account import Account
    from app.models.account_member import AccountMember
    from app.models.user import User

    acct = (
        await db.execute(select(Account).where(Account.slug == args.slug))
    ).scalar_one_or_none()
    user = (
        await db.execute(select(User).where(User.username == args.username))
    ).scalar_one_or_none()
    if not acct or not user:
        print("❌ 账户或用户不存在")
        return
    db.add(
        AccountMember(
            id=str(uuid.uuid4()),
            user_id=user.id,
            account_id=acct.id,
            role_in_account=args.role,
            joined_at=datetime.now(timezone.utc),
        )
    )
    await db.commit()
    print(f"✅ {args.username} 已添加到 {args.slug}")


async def _remove_member(args, db) -> None:
    """从账户移除成员。"""
    from app.models.account import Account
    from app.models.account_member import AccountMember
    from app.models.user import User
    from sqlalchemy import and_

    acct = (
        await db.execute(select(Account).where(Account.slug == args.slug))
    ).scalar_one_or_none()
    user = (
        await db.execute(select(User).where(User.username == args.username))
    ).scalar_one_or_none()
    if not acct or not user:
        print("❌ 账户或用户不存在")
        return
    m = (
        await db.execute(
            select(AccountMember).where(
                and_(
                    AccountMember.user_id == user.id,
                    AccountMember.account_id == acct.id,
                )
            )
        )
    ).scalar_one_or_none()
    if not m:
        print("❌ 成员关系不存在")
        return
    await db.delete(m)
    await db.commit()
    print(f"✅ {args.username} 已从 {args.slug} 移除")

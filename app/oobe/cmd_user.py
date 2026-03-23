"""user 子命令处理器。

支持 list / create / delete / ban / activate /
reset-password / set-role 操作。
"""

import asyncio
from sqlalchemy import select

_ACTIONS = [
    "list",
    "create",
    "delete",
    "ban",
    "activate",
    "reset-password",
    "set-role",
]


def handle_user(args) -> None:
    """分发用户管理操作。"""
    act = getattr(args, "user_action", None)
    if not act:
        print(f"请指定操作: {'/'.join(_ACTIONS)}")
        return
    asyncio.run(_dispatch(act, args))


async def _dispatch(act: str, args) -> None:
    """异步分发用户操作。"""
    from app.models.engine import AsyncSessionLocal
    from app.services.user.manager import list_users

    async with AsyncSessionLocal() as db:
        if act == "list":
            users, total = await list_users(db, limit=100)
            print(f"共 {total} 个用户:")
            for u in users:
                print(f"  {u.username} ({u.email}) [{u.role_code}]")
        elif act == "create":
            await _create(args, db)
        elif act in ("delete", "ban", "activate", "reset-password", "set-role"):
            await _modify(act, args, db)


async def _create(args, db) -> None:
    """创建新用户。"""
    from app.services.user.register import register_user

    try:
        user = await register_user(
            args.username,
            args.email,
            args.password,
            args.username,
            db,
        )
        if args.role != "normal":
            user.role_code = args.role
            await db.commit()
        print(f"✅ 用户 {user.username} 已创建")
    except ValueError as exc:
        print(f"❌ {exc}")


async def _modify(act, args, db) -> None:
    """修改用户状态/角色/密码。"""
    from app.models.user import User
    from app.services.crypto.hasher import hash_password

    user = (
        await db.execute(select(User).where(User.username == args.username))
    ).scalar_one_or_none()
    if not user:
        print(f"❌ 用户 {args.username} 不存在")
        return
    if act == "delete":
        await db.delete(user)
        print(f"✅ 用户 {args.username} 已删除")
    elif act == "ban":
        user.role_code = "banned"
        print(f"✅ 用户 {args.username} 已封禁")
    elif act == "activate":
        user.role_code = "normal"
        user.is_active = True
        print(f"✅ 用户 {args.username} 已激活")
    elif act == "reset-password":
        user.hashed_password = hash_password(args.password)
        print(f"✅ 用户 {args.username} 密码已重置")
    elif act == "set-role":
        user.role_code = args.role
        print(f"✅ 用户 {args.username} 角色设置为 {args.role}")
    await db.commit()

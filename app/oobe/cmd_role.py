"""role 子命令处理器。"""

import asyncio


def handle_role(args) -> None:
    """分发角色管理操作。"""
    act = getattr(args, "role_action", None)
    if not act:
        print("请指定操作: list / create / delete")
        return
    asyncio.run(_dispatch(act, args))


async def _dispatch(act, args) -> None:
    """异步分发角色操作。"""
    from app.models.engine import AsyncSessionLocal
    from app.services.user.role_manager import (
        list_roles,
        create_role,
        delete_role,
    )

    async with AsyncSessionLocal() as db:
        if act == "list":
            roles = await list_roles(db)
            for r in roles:
                s = " [系统]" if r.is_system else ""
                print(f"  {r.code} ({r.label}) P={r.priority}{s}")
        elif act == "create":
            await create_role(args.code, args.label, args.priority, db)
            print(f"✅ 角色 {args.code} 已创建")
        elif act == "delete":
            err = await delete_role(args.code, db)
            if err:
                print(f"❌ {err}")
            else:
                print(f"✅ 角色 {args.code} 已删除")

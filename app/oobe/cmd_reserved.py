"""reserved-name 子命令处理器。"""

import asyncio
from sqlalchemy import select


def handle_reserved(args) -> None:
    """分发保留名管理操作。"""
    act = getattr(args, "reserved_action", None)
    if not act:
        print("请指定操作: list / add")
        return
    asyncio.run(_dispatch(act, args))


async def _dispatch(act, args) -> None:
    """异步分发保留名操作。"""
    from app.models.engine import AsyncSessionLocal
    from app.models.reserved_name import ReservedName

    async with AsyncSessionLocal() as db:
        if act == "list":
            r = await db.execute(select(ReservedName))
            names = r.scalars().all()
            print(f"共 {len(names)} 个保留名:")
            for n in names:
                print(f"  {n.name}")
        elif act == "add":
            db.add(ReservedName(name=args.name, reason="手动添加"))
            await db.commit()
            print(f"✅ 保留名 {args.name} 已添加")

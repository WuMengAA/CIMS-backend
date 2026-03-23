"""quota 子命令处理器。"""

import asyncio


def handle_quota(args) -> None:
    """分发限额管理操作。"""
    act = getattr(args, "quota_action", None)
    if not act:
        print("请指定操作: list / set")
        return
    asyncio.run(_dispatch(act, args))


async def _dispatch(act, args) -> None:
    """异步分发限额操作。"""
    from app.models.engine import AsyncSessionLocal
    from app.services.quota.manager import get_quotas, set_quota

    async with AsyncSessionLocal() as db:
        if act == "list":
            qs = await get_quotas(args.account, db)
            if not qs:
                print("无限额配置")
            for q in qs:
                print(f"  {q.quota_key}: {q.current_value}/{q.max_value}")
        elif act == "set":
            await set_quota(args.account, args.key, args.value, db)
            print(f"✅ {args.key} = {args.value}")

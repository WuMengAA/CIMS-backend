"""config 子命令处理器。"""

import asyncio
from sqlalchemy import select
from datetime import datetime, timezone


def handle_config(args) -> None:
    """分发配置管理操作。"""
    act = getattr(args, "config_action", None)
    if not act:
        print("请指定操作: get / set")
        return
    asyncio.run(_dispatch(act, args))


async def _dispatch(act, args) -> None:
    """异步分发配置操作。"""
    from app.models.engine import AsyncSessionLocal
    from app.models.system_config import SystemConfig

    async with AsyncSessionLocal() as db:
        if act == "get":
            r = await db.execute(
                select(SystemConfig).where(SystemConfig.key == args.key)
            )
            cfg = r.scalar_one_or_none()
            if cfg:
                print(f"{cfg.key} = {cfg.value}")
            else:
                print(f"配置 {args.key} 不存在")
        elif act == "set":
            r = await db.execute(
                select(SystemConfig).where(SystemConfig.key == args.key)
            )
            cfg = r.scalar_one_or_none()
            now = datetime.now(timezone.utc)
            if cfg:
                cfg.value = args.value
                cfg.updated_at = now
            else:
                db.add(
                    SystemConfig(
                        key=args.key,
                        value=args.value,
                        updated_at=now,
                    )
                )
            await db.commit()
            print(f"✅ {args.key} = {args.value}")

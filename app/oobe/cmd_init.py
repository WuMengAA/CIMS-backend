"""init 子命令处理器。"""

import asyncio


def handle_init() -> None:
    """处理 `cims init` 子命令。"""
    from app.oobe.detector import is_initialized, confirm_reinit
    from app.oobe.prompts import collect_config
    from app.oobe.initializer import write_config_file, init_database

    if is_initialized():
        if not confirm_reinit():
            print("已取消初始化。")
            return
    config = collect_config()
    write_config_file(config)
    asyncio.run(init_database(config))

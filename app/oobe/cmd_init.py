"""init 子命令处理器。

执行系统初始化并生成 systemd 服务文件。
"""

import asyncio


def handle_init() -> None:
    """处理 `cims init` 子命令。

    流程：
      1. 检测是否已初始化（已初始化则要求确认）
      2. 交互式收集配置信息
      3. 写入配置文件
      4. 初始化数据库
      5. 生成 systemd 服务文件并尝试安装
    """
    from app.oobe.detector import is_initialized, confirm_reinit
    from app.oobe.prompts import collect_config
    from app.oobe.initializer import (
        write_config_file,
        init_database,
        generate_systemd_service,
    )

    if is_initialized():
        if not confirm_reinit():
            print("已取消初始化。")
            return
    config = collect_config()
    write_config_file(config)
    asyncio.run(init_database(config))
    generate_systemd_service()

"""serve 子命令处理器。"""

import asyncio
import sys


def handle_serve() -> None:
    """处理 `cims serve` 子命令。"""
    from app.oobe.detector import is_initialized

    if not is_initialized():
        print("❌ 系统尚未初始化。请先运行: uv run cims init")
        sys.exit(1)
    from app.main import _start_servers

    asyncio.run(_start_servers())

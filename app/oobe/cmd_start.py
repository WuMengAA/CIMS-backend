"""start 子命令处理器。

通过 systemctl 启动 cims-backend 服务。
"""

import subprocess
import sys


def handle_start() -> None:
    """处理 `cims start` 子命令。

    调用 systemctl start cims-backend 启动服务。
    若非 root 则自动使用 sudo。
    """
    _run_systemctl("start")


def _run_systemctl(action: str) -> None:
    """执行 systemctl 命令。

    Args:
        action: systemctl 动作，如 start / stop / enable / disable。
    """
    import os

    cmd = ["systemctl", action, "cims-backend"]
    if os.geteuid() != 0:
        cmd = ["sudo"] + cmd

    print(f"⏳ 正在执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ cims-backend 已{_action_label(action)}")
    else:
        print(f"❌ 操作失败: {result.stderr.strip()}")
        sys.exit(1)


def _action_label(action: str) -> str:
    """将 systemctl 动作转换为中文标签。

    Args:
        action: systemctl 动作字符串。

    Returns:
        对应的中文标签。
    """
    labels = {
        "start": "启动",
        "stop": "停止",
        "enable": "设为开机自启",
        "disable": "取消开机自启",
    }
    return labels.get(action, action)

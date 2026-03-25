"""stop 子命令处理器。

通过 systemctl 停止 cims-backend 服务。
"""

import subprocess
import sys


def handle_stop() -> None:
    """处理 `cims stop` 子命令。

    调用 systemctl stop cims-backend 停止服务。
    若非 root 则自动使用 sudo。
    """
    import os

    cmd = ["systemctl", "stop", "cims-backend"]
    if os.geteuid() != 0:
        cmd = ["sudo"] + cmd

    print(f"⏳ 正在执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ cims-backend 已停止")
    else:
        print(f"❌ 停止失败: {result.stderr.strip()}")
        sys.exit(1)

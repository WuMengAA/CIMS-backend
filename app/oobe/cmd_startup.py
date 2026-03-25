"""startup 子命令处理器。

切换 cims-backend 开机自启动状态。
"""

import subprocess
import sys


def handle_startup() -> None:
    """处理 `cims startup` 子命令。

    检测当前开机自启状态，若已启用则禁用，否则启用。
    相当于开关切换。
    """
    import os

    # 检测当前状态
    check = subprocess.run(
        ["systemctl", "is-enabled", "cims-backend"],
        capture_output=True,
        text=True,
    )
    currently_enabled = check.stdout.strip() == "enabled"

    if currently_enabled:
        action = "disable"
        label = "取消开机自启"
    else:
        action = "enable"
        label = "设为开机自启"

    cmd = ["systemctl", action, "cims-backend"]
    if os.geteuid() != 0:
        cmd = ["sudo"] + cmd

    print(f"⏳ 正在{label}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        new_state = "已启用 ✅" if action == "enable" else "已禁用 ⬚"
        print(f"开机自启: {new_state}")
    else:
        print(f"❌ 操作失败: {result.stderr.strip()}")
        sys.exit(1)

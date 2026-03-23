"""OOBE 初始化检测器。

检测 .cims/config.json 是否存在以判断是否需要运行初始化。
已有配置时提示将删除所有数据并要求确认。
"""

from pathlib import Path

# 配置文件路径
CONFIG_DIR = Path(".cims")
CONFIG_FILE = CONFIG_DIR / "config.json"


def is_initialized() -> bool:
    """检测系统是否已完成初始化。"""
    return CONFIG_FILE.exists()


def confirm_reinit() -> bool:
    """已有配置时要求用户确认重新初始化。

    Returns:
        True 表示用户确认继续，False 表示取消。
    """
    print("\n⚠️  检测到已有初始化配置。")
    print("重新初始化将 删除所有数据 并重建数据库。")
    answer = input("确认继续？(yes/NO): ").strip().lower()
    return answer == "yes"

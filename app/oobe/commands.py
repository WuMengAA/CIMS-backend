"""CLI 子命令分发器。

将 argparse 解析结果路由到对应的命令处理函数。
"""

import sys


def dispatch(args) -> None:
    """根据子命令分发到对应处理器。"""
    cmd = args.command
    handlers = {
        "init": _h_init,
        "serve": _h_serve,
        "status": _h_status,
        "version": _h_version,
        "user": _h_user,
        "account": _h_account,
        "role": _h_role,
        "quota": _h_quota,
        "config": _h_config,
        "reserved-name": _h_reserved,
        "db-migrate": _h_migrate,
    }
    h = handlers.get(cmd)
    if h:
        h(args)
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)


def _h_init(_a):
    """处理 init 子命令。"""
    from app.oobe.cmd_init import handle_init

    handle_init()


def _h_serve(_a):
    """处理 serve 子命令。"""
    from app.oobe.cmd_serve import handle_serve

    handle_serve()


def _h_status(_a):
    """检查系统状态。"""
    from app.oobe.detector import is_initialized

    s = "✅ 已初始化" if is_initialized() else "❌ 未初始化"
    print(s)


def _h_version(_a):
    """显示版本号。"""
    print("CIMS Backend v0.1.0")


def _h_user(a):
    """用户管理子命令。"""
    from app.oobe.cmd_user import handle_user

    handle_user(a)


def _h_account(a):
    """账户管理子命令。"""
    from app.oobe.cmd_account import handle_account

    handle_account(a)


def _h_role(a):
    """角色管理子命令。"""
    from app.oobe.cmd_role import handle_role

    handle_role(a)


def _h_quota(a):
    """限额管理子命令。"""
    from app.oobe.cmd_quota import handle_quota

    handle_quota(a)


def _h_config(a):
    """配置管理子命令。"""
    from app.oobe.cmd_config import handle_config

    handle_config(a)


def _h_reserved(a):
    """保留名管理子命令。"""
    from app.oobe.cmd_reserved import handle_reserved

    handle_reserved(a)


def _h_migrate(_a):
    """执行数据库迁移。"""
    import subprocess

    subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        check=True,
    )

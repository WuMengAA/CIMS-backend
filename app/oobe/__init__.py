"""CIMS 统一 CLI 入口。

提供 20+ 子命令覆盖用户、账户、角色、限额、配置和保留名管理。
无参数运行时显示帮助信息。
"""

import argparse
import sys


def _build_parser() -> argparse.ArgumentParser:
    """构建 CLI 参数解析器。"""
    from app.oobe.cli_parser import build_parser

    return build_parser()


def main():
    """CLI 主入口函数。"""
    parser = _build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)
    from app.oobe.commands import dispatch

    dispatch(args)

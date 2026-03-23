"""OOBE CLI 交互式问询。

依次询问数据库连接、超级管理员信息等，
默认值从 .env 环境变量读取。
"""

import os
from .validator import (
    validate_db_url,
    validate_email,
    validate_password,
    validate_username,
)


def _ask(prompt: str, default: str = "", validator=None) -> str:
    """通用输入问询，带默认值和可选验证。"""
    while True:
        hint = f" [{default}]" if default else ""
        answer = input(f"{prompt}{hint}: ").strip() or default
        if validator:
            err = validator(answer)
            if err:
                print(f"  ❌ {err}")
                continue
        return answer


def collect_config() -> dict:
    """交互式收集所有必要配置信息。

    Returns:
        包含 db_url, redis_url, username, email, password 等的字典。
    """
    print("\n🚀 CIMS 初始化向导\n")
    print("=" * 50)
    # 数据库连接
    db_url = _ask(
        "PostgreSQL 连接 URL",
        os.environ.get(
            "DATABASE_URL",
            "postgresql+psycopg://postgres:password@localhost:5432/cims",
        ),
        validate_db_url,
    )
    # Redis 连接
    redis_url = _ask(
        "Redis 连接 URL",
        os.environ.get("REDIS_URL", "redis://:password@localhost:6379/0"),
    )
    print("\n--- 超级管理员账户 ---")
    username = _ask("用户名", "admin", validate_username)
    email = _ask("邮箱", "", validate_email)
    password = _ask("密码（≥12位）", "", validate_password)
    # 域名与端口
    print("\n--- 服务配置 ---")
    domain = _ask("基础域名", os.environ.get("CIMS_BASE_DOMAIN", "miniclassisland.com"))
    return {
        "db_url": db_url,
        "redis_url": redis_url,
        "username": username,
        "email": email,
        "password": password,
        "domain": domain,
    }

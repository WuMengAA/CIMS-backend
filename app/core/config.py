"""全局应用配置。

配置优先级：.cims/config.json > .env > 环境变量。
.cims/config.json 仅存储数据库连接信息。
其他配置存储在元数据数据库的 system_config 表中。
"""

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# ---- .env 文件自动加载 ----
_ENV_FILE = Path(".env")


def _load_dotenv() -> None:
    """读取 .env 文件，仅在键不存在时设置环境变量。"""
    if not _ENV_FILE.exists():
        return
    with open(_ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            os.environ.setdefault(key, value)


_load_dotenv()

# ---- .cims/config.json ----
_CONFIG_DIR = Path(".cims")
_CONFIG_FILE = _CONFIG_DIR / "config.json"


def _load_file_config() -> dict:
    """从 .cims/config.json 加载数据库连接配置。"""
    if _CONFIG_FILE.exists():
        with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


_file_cfg = _load_file_config()

# ---- 数据库 / Redis（允许为空，启动服务前由 validate_config 校验）----
DATABASE_URL: str = _file_cfg.get(
    "database_url",
    os.environ.get("DATABASE_URL", ""),
)

REDIS_URL: str = os.environ.get("REDIS_URL", "")

# Redis 逻辑 DB 分配
REDIS_DB_AUTH: int = 0
REDIS_DB_SESSION: int = 1
REDIS_DB_CACHE: int = 2

# 多租户托管配置
BASE_DOMAIN: str = os.environ.get("CIMS_BASE_DOMAIN", "miniclassisland.com")
DEFAULT_SCHEMA: str = "public"

# 分区服务端口分配
CLIENT_PORT: int = int(os.environ.get("CIMS_CLIENT_PORT", "50050"))
ADMIN_PORT: int = int(os.environ.get("CIMS_ADMIN_PORT", "50051"))
GRPC_PORT: int = int(os.environ.get("CIMS_GRPC_PORT", "50052"))

# GPG 密钥文件路径
KEY_FILE: str = os.environ.get("CIMS_KEY_FILE", "cims_server.key")


def validate_config() -> None:
    """在服务启动前校验关键配置，缺失时快速失败。

    仅由 serve 命令调用——init / help 等 CLI 子命令不会触发此检查。
    """
    if not DATABASE_URL:
        raise RuntimeError(
            "必须通过 .cims/config.json、.env 或 DATABASE_URL 环境变量提供数据库连接"
        )
    if not REDIS_URL:
        raise RuntimeError(
            "必须通过 .env 或 REDIS_URL 环境变量提供 Redis 连接"
        )

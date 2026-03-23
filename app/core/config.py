"""全局应用配置。

配置优先级：.cims/config.json > .env > 硬编码默认值。
.cims/config.json 仅存储数据库连接信息。
其他配置存储在元数据数据库的 system_config 表中。
"""

import json
import os
from pathlib import Path

# .cims/config.json 路径
_CONFIG_DIR = Path(".cims")
_CONFIG_FILE = _CONFIG_DIR / "config.json"


def _load_file_config() -> dict:
    """从 .cims/config.json 加载数据库连接配置。"""
    if _CONFIG_FILE.exists():
        with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


_file_cfg = _load_file_config()

# 数据库连接（优先 config.json，其次 .env）
DATABASE_URL: str = _file_cfg.get(
    "database_url",
    os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:password@localhost:5432/cims",
    ),
)

# Redis 连接
REDIS_URL: str = os.environ.get("REDIS_URL", "redis://:password@localhost:6379/0")

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

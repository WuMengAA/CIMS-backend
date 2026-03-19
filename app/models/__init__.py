"""CIMS 数据库模型聚合。

集中暴露所有实体模型，以便在整个项目内实现整洁的导入。
"""

from .base import Base
from .tenant import Tenant
from .resource_files import (
    CPFile,
    TLFile,
    SubFile,
    PolicyFile,
    SettingsFile,
    ComponentsFile,
    CredentialsFile,
)
from .client import ClientRecord, ClientProfile
from .audit import AuditLog
from .config_upload import ConfigUploadRecord
from .engine import AsyncSessionLocal, init_db
from .session import get_db

__all__ = [
    "Base",
    "Tenant",
    "CPFile",
    "TLFile",
    "SubFile",
    "PolicyFile",
    "SettingsFile",
    "ComponentsFile",
    "CredentialsFile",
    "ClientRecord",
    "ClientProfile",
    "AuditLog",
    "ConfigUploadRecord",
    "AsyncSessionLocal",
    "init_db",
    "get_db",
]

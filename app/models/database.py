"""数据库模型 Facade 索引。

该文件作为一个向后兼容层，将所有分散的模型及引擎实例归集至此。
新开发的功能建议直接从 app.models 子包导入各实体。
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

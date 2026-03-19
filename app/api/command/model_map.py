"""资源映射配置。

定义了公开资源类型字符串与后端 SQLAlchemy 模型类之间的映射，
用于动态处理不同类型的配置管理。
"""

from app.models.database import (
    CPFile,
    TLFile,
    SubFile,
    PolicyFile,
    SettingsFile,
    ComponentsFile,
    CredentialsFile,
)

# 资源类型到数据库模型的映射表
MODEL_MAP = {
    "ClassPlan": CPFile,
    "TimeLayout": TLFile,
    "Subjects": SubFile,
    "Policy": PolicyFile,
    "DefaultSettings": SettingsFile,
    "Components": ComponentsFile,
    "Credentials": CredentialsFile,
}

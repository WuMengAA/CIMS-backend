"""配置与媒体资源的数据库存储定义。

利用共有 Mixin 实现了 CP, TL, Subjects, Policy, Settings, Components, Credentials 具体的表实体。
"""

from .base import Base
from .resource_mixin import ResourceMixin


class CPFile(Base, ResourceMixin):
    __tablename__ = "cp_files"


class TLFile(Base, ResourceMixin):
    __tablename__ = "tl_files"


class SubFile(Base, ResourceMixin):
    __tablename__ = "sub_files"


class PolicyFile(Base, ResourceMixin):
    __tablename__ = "policy_files"


class SettingsFile(Base, ResourceMixin):
    __tablename__ = "settings_files"


class ComponentsFile(Base, ResourceMixin):
    __tablename__ = "components_files"


class CredentialsFile(Base, ResourceMixin):
    __tablename__ = "credentials_files"

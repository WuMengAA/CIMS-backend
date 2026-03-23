"""配置与媒体资源的数据库存储定义。

利用共有 Mixin 实现了 CP, TL, Subjects, Policy, Settings, Components, Credentials 具体的表实体。
"""

from .base import Base
from .resource_mixin import ResourceMixin


class CPFile(Base, ResourceMixin):
    """课程计划资源文件表。"""

    __tablename__ = "cp_files"


class TLFile(Base, ResourceMixin):
    """时间布局资源文件表。"""

    __tablename__ = "tl_files"


class SubFile(Base, ResourceMixin):
    """科目资源文件表。"""

    __tablename__ = "sub_files"


class PolicyFile(Base, ResourceMixin):
    """策略资源文件表。"""

    __tablename__ = "policy_files"


class SettingsFile(Base, ResourceMixin):
    """默认设置资源文件表。"""

    __tablename__ = "settings_files"


class ComponentsFile(Base, ResourceMixin):
    """组件资源文件表。"""

    __tablename__ = "components_files"


class CredentialsFile(Base, ResourceMixin):
    """凭据资源文件表。"""

    __tablename__ = "credentials_files"

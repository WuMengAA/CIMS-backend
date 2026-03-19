"""数据库基类模型定义。

声明了项目中所有模型通用的 SQLAlchemy DeclarativeBase。
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """CIMS 所有数据库模型的共有基类。"""

    pass

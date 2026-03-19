"""批量操作定义。

允许在单次请求中对多个资源进行创建、写入和删除。
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class BatchOpType(str, Enum):
    """支持的操作原子类型。"""

    create = "create"
    write = "write"
    update = "update"
    delete = "delete"


class BatchOperation(BaseModel):
    """单条操作请求的包装器。"""

    action: BatchOpType
    resource_type: str
    name: str
    payload: Optional[Dict[str, Any]] = None


class BatchRequest(BaseModel):
    """A collection of operations to be executed atomically."""

    operations: List[BatchOperation]

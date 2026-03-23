"""批量操作定义。

允许在单次请求中对多个资源进行创建、写入和删除。
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BatchOpType(str, Enum):
    """支持的操作原子类型。"""

    create = "create"
    write = "write"
    update = "update"
    delete = "delete"


class BatchOperation(BaseModel):
    """单条操作请求的包装器。"""

    action: BatchOpType
    resource_type: str = Field(..., max_length=64)
    name: str = Field(..., max_length=255)
    payload: Optional[Dict[str, Any]] = None


class BatchRequest(BaseModel):
    """需要原子执行的操作集合。"""

    operations: List[BatchOperation] = Field(..., max_length=100)


# 向后兼容别名
BatchOperationAction = BatchOpType

"""版本冲突检测工具。

在并发写入场景下对资源版本号进行乐观锁校验。
"""

from fastapi import HTTPException
from typing import Optional


def check_version(record, client_version: Optional[int]) -> None:
    """校验客户端提供的版本号是否与数据库一致。

    Args:
        record: 数据库中的现有记录。
        client_version: 客户端提供的期望版本号，为 None 时跳过。

    Raises:
        HTTPException: 版本不匹配时抛出 409 Conflict。
    """
    if client_version is None:
        return
    if record.version != client_version:
        raise HTTPException(
            status_code=409,
            detail=f"版本冲突：服务端={record.version}, 客户端={client_version}",
        )

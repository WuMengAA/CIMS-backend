"""请求负载校验工具。

限制 JSON payload 的总大小和嵌套深度，防止解析拒绝服务。
"""

import json
from fastapi import HTTPException

# 安全限制常量
MAX_PAYLOAD_BYTES = 512 * 1024  # 512 KB
MAX_NESTING_DEPTH = 10


def _check_depth(obj, current: int = 0) -> int:
    """递归检查嵌套深度，超限时抛出异常。"""
    if current > MAX_NESTING_DEPTH:
        raise HTTPException(status_code=400, detail="嵌套深度超限")
    if isinstance(obj, dict):
        for v in obj.values():
            _check_depth(v, current + 1)
    elif isinstance(obj, list):
        for item in obj:
            _check_depth(item, current + 1)
    return current


def validate_payload(payload: dict) -> None:
    """校验 payload 大小和嵌套深度。"""
    raw = json.dumps(payload, ensure_ascii=False)
    if len(raw.encode("utf-8")) > MAX_PAYLOAD_BYTES:
        raise HTTPException(status_code=400, detail="载荷体积超过 512KB 限制")
    _check_depth(payload)

"""gRPC 辅助工具。

封装用于提取 gRPC 元数据及租户上下文的公共便捷方法。
"""

import grpc
from app.core.tenant.context import get_tenant_id


def get_metadata_dict(context: grpc.aio.ServicerContext) -> dict:
    """将 gRPC 调用的元数据转换为字典格式。"""
    return dict(context.invocation_metadata())


def get_tenant_id_safe() -> str:
    """安全获取当前上下文中的租户 ID，不存在则返回空。"""
    try:
        return get_tenant_id()
    except RuntimeError:
        return ""

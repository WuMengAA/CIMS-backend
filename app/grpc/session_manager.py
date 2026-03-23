"""兼容层：保留旧版 session_manager 模块路径。

重构后 SessionManager 移至 app.grpc.session.manager，此模块仅做重导出。
"""

from .session.manager import SessionManager  # noqa: F401
from .session.peer_parser import parse_grpc_peer_ip  # noqa: F401

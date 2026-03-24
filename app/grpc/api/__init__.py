"""gRPC Protobuf API 包。

将当前目录加入 sys.path 以解决 protoc 生成代码的导入路径问题。
protoc 生成的代码使用 `from Protobuf.Enum import ...` 形式的绝对导入，
需要此目录在 sys.path 中才能正确解析。
"""

import sys
from pathlib import Path

_api_dir = str(Path(__file__).resolve().parent)
if _api_dir not in sys.path:
    sys.path.insert(0, _api_dir)

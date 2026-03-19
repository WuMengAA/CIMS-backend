"""HTTP 和 gRPC 协议共用的认证辅助工具。"""

from fastapi import Request


def extract_bearer(request: Request) -> str:
    """从 Authorization 标头中提取 Bearer 令牌。

    参数:
        request: 传入的 FastAPI/Starlette 请求对象。

    返回:
        如果符合标准 Bearer 格式，则返回令牌部分，否则返回空字符串。
    """
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return ""

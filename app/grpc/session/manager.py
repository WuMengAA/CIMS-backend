"""Cyrene_MSP 会话管理器入口。

组合密钥系统、握手协议及在线状态，为 gRPC Servicer 提供统一接口。
"""

import os
from .key_management import GPGKeyManager
from .handshake_state import store_handshake_challenge, pop_handshake_challenge
from .session_state import create_new_session, get_session_info
from . import online_status

KEY_FILE = os.environ.get("CIMS_KEY_FILE", "cims_server.key")


class SessionManager:
    """核心会话逻辑封装类。"""

    def __init__(self, key_path: str = KEY_FILE, *, key_file: str | None = None):
        path = key_file or key_path
        self._km = GPGKeyManager(path)
        self.public_key_armor = self._km.public_key_armor
        self._private_key = self._km.private_key

    def decrypt_challenge(self, token):
        """解密挑战令牌。"""
        if self._private_key is None:
            return None
        return self._km.decrypt(token)

    async def store_pending_handshake(self, tid, cuid, token):
        """记录待办握手。"""
        await store_handshake_challenge(tid, cuid, token)

    async def pop_handshake_challenge(self, tid, cuid):
        """提取并销毁待确认的挑战令牌。"""
        return await pop_handshake_challenge(tid, cuid)

    async def create_session(self, tid, cuid):
        """创建新会话并返回 session ID。"""
        return await create_new_session(tid, cuid)

    async def complete_handshake(self, tid, cuid, accepted):
        """兼容旧版：验证挑战令牌并颁发会话。"""
        pending = await pop_handshake_challenge(tid, cuid)
        return await create_new_session(tid, cuid) if pending and accepted else None

    async def validate_session(self, sid):
        """根据 Session ID 查询关联的客户端 UID。"""
        return (await get_session_info(sid)).get("cuid")

    async def get_session_tenant(self, sid):
        """根据 Session ID 查询关联的租户 ID。"""
        return (await get_session_info(sid)).get("tenant_id")

    async def set_client_online(self, tid, cuid, ip=""):
        """标记指定客户端上线并记录 IP 地址。"""
        await online_status.set_online(tid, cuid, ip)

    async def set_client_offline(self, tid, cuid):
        """标记指定客户端离线。"""
        await online_status.set_offline(tid, cuid)

    async def get_all_clients_status(self, tid):
        """获取租户下所有客户端的在线状态列表。"""
        return await online_status.get_full_client_status(tid)

    async def get_all_online_ips(self, tid):  # pragma: no cover
        """获取租户下所有在线客户端的 IP 集合。"""
        return await online_status.get_tenant_online_ips(tid)

    async def is_client_online(self, tid, cuid):
        """检查指定客户端是否在线。"""
        from app.core.config import REDIS_DB_SESSION
        from app.core.redis.accessor import get_redis

        return await get_redis(REDIS_DB_SESSION).exists(f"online:{tid}:{cuid}") > 0

    async def update_heartbeat(self, tid, cuid):
        """刷新客户端心跳，延长在线状态有效期。"""
        await online_status.set_online(tid, cuid, "")

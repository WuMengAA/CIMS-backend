"""Cyrene_MSP 会话管理器入口。

组合密钥系统、握手协议及在线状态，为 gRPC Servicer 提供统一的领域接口。
"""

import os
from .key_management import GPGKeyManager
from .handshake_state import store_handshake_challenge, pop_handshake_challenge
from .session_state import create_new_session, get_session_info
from . import online_status

KEY_FILE = os.environ.get("CIMS_KEY_FILE", "cims_server.key")


class SessionManager:
    """核心会话逻辑封装类。"""

    def __init__(self, key_path: str = KEY_FILE):
        self._km = GPGKeyManager(key_path)
        self.public_key_armor = self._km.public_key_armor

    def decrypt_challenge(self, token):
        """解密令牌接口。"""
        return self._km.decrypt(token)

    async def store_pending_handshake(self, tid, cuid, token):
        """记录待办握手。"""
        await store_handshake_challenge(tid, cuid, token)

    async def complete_handshake(self, tid, cuid, accepted):
        """验证挑战令牌并颁发会话。"""
        pending = await pop_handshake_challenge(tid, cuid)
        return await create_new_session(tid, cuid) if pending and accepted else None

    # 导出状态检测方法 (适配旧版 Server.py 结构)
    async def validate_session(self, sid):
        return (await get_session_info(sid)).get("cuid")

    async def get_session_tenant(self, sid):
        return (await get_session_info(sid)).get("tenant_id")

    async def set_client_online(self, tid, cuid, ip=""):
        await online_status.set_online(tid, cuid, ip)

    async def set_client_offline(self, tid, cuid):
        await online_status.set_offline(tid, cuid)

    async def get_all_clients_status(self, tid):
        return await online_status.get_full_client_status(tid)

    async def get_all_online_ips(self, tid):
        return await online_status.get_tenant_online_ips(tid)

    async def is_client_online(self, tid, cuid):
        from app.core.redis.accessor import get_redis

        return await get_redis().exists(f"online:{tid}:{cuid}") > 0

    async def update_heartbeat(self, tid, cuid):
        await online_status.set_online(tid, cuid, "")

"""终端在线心跳状态检测。

利用 Redis 实现分布式的在线状态维持、IP 抓取以及租户维度的批量查询。
"""

from app.core.redis.accessor import get_redis
from .peer_parser import parse_grpc_peer_ip

ONLINE_TTL = 60


async def set_online(tid: str, cuid: str, ip_raw: str = ""):
    """标记客户端在线并记录 IP。"""
    rd = get_redis()
    key = f"online:{tid}:{cuid}"
    await rd.hset(key, mapping={"status": "online", "ip": ip_raw})
    await rd.expire(key, ONLINE_TTL)


async def set_offline(tid: str, cuid: str):
    """显式移除客户端在线记录。"""
    await get_redis().delete(f"online:{tid}:{cuid}")


async def get_tenant_online_ips(tid: str) -> set[str]:
    """获取指定租户下所有在线客户端的清洗后 IP 集合。"""
    rd, prefix = get_redis(), f"online:{tid}:"
    ips = set()
    async for key in rd.scan_iter(match=f"{prefix}*"):
        data = await rd.hgetall(key)
        ip = parse_grpc_peer_ip(data.get("ip", ""))
        if ip:
            ips.add(ip)
    return ips


async def get_full_client_status(tid: str) -> list:
    """获取租户下所有设备状态（用于控制台展示）。"""
    rd, prefix = get_redis(), f"online:{tid}:"
    res = []
    async for key in rd.scan_iter(match=f"{prefix}*"):
        data = await rd.hgetall(key)
        res.append(
            {"uid": key[len(prefix) :], "status": "online", "ip": data.get("ip", "")}
        )
    return res

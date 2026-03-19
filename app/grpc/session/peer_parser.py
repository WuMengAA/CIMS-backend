"""gRPC 对端 IP 解析逻辑。

提供针对 IPv4 和 IPv6 格式的 Peer 字符串清洗，确保 IP 绑定的准确性。
"""


def parse_grpc_peer_ip(peer: str) -> str:
    """提取对端 IP 部分（剔除特定协议前缀与端口号）。"""
    if not peer:
        return ""

    # 处理 IPv4 (ipv4:1.2.3.4:5678)
    if peer.startswith("ipv4:"):
        return peer[5:].rsplit(":", 1)[0]

    # 处理 IPv6 (ipv6:[::1]:5678)
    if peer.startswith("ipv6:"):
        inner = peer[5:]
        if inner.startswith("["):
            return inner[1 : inner.index("]")]
        return inner.rsplit(":", 1)[0]

    return peer

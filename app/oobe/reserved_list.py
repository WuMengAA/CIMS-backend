"""系统保留名称完整列表。

覆盖 9 个分类共 150+ 条目，防止用户名和 Slug 与系统路由冲突。
"""

# 基础协议与网络服务
_PROTOCOL = [
    "admin",
    "api",
    "www",
    "mail",
    "ftp",
    "ssh",
    "dns",
    "smtp",
    "pop",
    "imap",
    "ntp",
    "snmp",
    "ldap",
    "tcp",
    "udp",
    "http",
    "https",
    "ssl",
    "tls",
    "vpn",
    "proxy",
]

# 认证与授权
_AUTH = [
    "login",
    "logout",
    "register",
    "signup",
    "signin",
    "auth",
    "oauth",
    "oauth2",
    "openid",
    "sso",
    "saml",
    "2fa",
    "mfa",
    "totp",
    "otp",
    "token",
    "session",
    "password",
    "passwd",
    "reset",
    "verify",
    "activate",
    "deactivate",
    "confirm",
    "callback",
    "redirect",
]

# 管理面板
_ADMIN = [
    "dashboard",
    "panel",
    "console",
    "manage",
    "management",
    "billing",
    "settings",
    "config",
    "configuration",
    "control",
    "monitor",
    "analytics",
    "metrics",
    "logs",
    "admin",
    "superadmin",
    "moderator",
    "operator",
]

# 系统关键词
_SYSTEM = [
    "system",
    "root",
    "null",
    "undefined",
    "localhost",
    "cims",
    "server",
    "node",
    "cluster",
    "master",
    "slave",
    "worker",
    "daemon",
    "cron",
    "scheduler",
    "queue",
    "cache",
    "redis",
    "postgres",
    "database",
    "db",
    "env",
    "debug",
    "staging",
    "production",
    "dev",
    "test",
    "testing",
    "sandbox",
    "preview",
    "canary",
]

# 静态资源
_RESOURCE = [
    "cdn",
    "static",
    "assets",
    "media",
    "upload",
    "uploads",
    "download",
    "downloads",
    "files",
    "images",
    "img",
    "css",
    "js",
    "fonts",
    "icons",
    "favicon",
    "robots",
    "sitemap",
    "manifest",
    "sw",
    "service-worker",
]

# API 端点
_API = [
    "grpc",
    "ws",
    "wss",
    "websocket",
    "graphql",
    "webhook",
    "webhooks",
    "rest",
    "rpc",
    "v1",
    "v2",
    "v3",
    "v4",
    "health",
    "healthcheck",
    "ping",
    "pong",
    "heartbeat",
    "status",
    "info",
    "version",
    "about",
    "docs",
    "spec",
]

# 社交与用户
_SOCIAL = [
    "profile",
    "account",
    "accounts",
    "user",
    "users",
    "team",
    "teams",
    "org",
    "organization",
    "group",
    "groups",
    "member",
    "members",
    "invite",
    "invites",
    "join",
    "follow",
    "followers",
    "following",
    "feed",
    "activity",
    "notification",
    "notifications",
    "message",
    "messages",
]

# 安全
_SECURITY = [
    "security",
    "abuse",
    "spam",
    "phishing",
    "malware",
    "virus",
    "report",
    "block",
    "ban",
    "suspend",
    "blacklist",
    "whitelist",
    "allowlist",
    "denylist",
    "captcha",
    "challenge",
    "audit",
    "compliance",
]

# 品牌与产品
_BRAND = [
    "classisland",
    "miniclassisland",
    "island",
    "ci",
    "class",
    "school",
    "campus",
    "education",
    "edu",
    "student",
    "teacher",
    "classroom",
    "lesson",
    "course",
]

# 通用保留
_MISC = [
    "demo",
    "example",
    "sample",
    "support",
    "help",
    "faq",
    "blog",
    "news",
    "press",
    "legal",
    "terms",
    "privacy",
    "policy",
    "copyright",
    "trademark",
    "contact",
    "home",
    "index",
    "main",
    "app",
    "application",
    "service",
    "store",
    "shop",
    "marketplace",
    "plugin",
    "plugins",
    "extension",
    "extensions",
    "theme",
    "themes",
    "public",
    "private",
    "internal",
    "external",
    "new",
    "create",
    "edit",
    "delete",
    "remove",
    "update",
    "search",
    "explore",
    "discover",
    "trending",
    "popular",
]

# 汇总导出
RESERVED_NAMES: list[str] = sorted(
    set(
        _PROTOCOL
        + _AUTH
        + _ADMIN
        + _SYSTEM
        + _RESOURCE
        + _API
        + _SOCIAL
        + _SECURITY
        + _BRAND
        + _MISC
    )
)

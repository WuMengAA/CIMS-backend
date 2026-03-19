# CIMS Backend

> ClassIsland Management Server（集控服务器）— Python 实现  
> 基于 [Cyrene_MSP 协议 v2.0.0.0](https://github.com/ClassIsland/ClassIsland/tree/master/doc/Design/Cyrene_MSP)

[![Python CI](https://github.com/MINIOpenSource/CIMS-backend/actions/workflows/python-ci.yml/badge.svg)](https://github.com/MINIOpenSource/CIMS-backend/actions/workflows/python-ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-green)](LICENSE)

---

## 概述

CIMS-backend 是 [ClassIsland](https://github.com/ClassIsland/ClassIsland) 的集中管理服务端，为教育场景提供多租户校园终端管理能力。它通过 HTTP API 与 gRPC 双通道同时服务客户端和管理后台，实现课表分发、远程指令下发、配置同步、审计日志等核心功能。

## 技术栈

| 组件 | 技术 |
|------|------|
| HTTP API | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) |
| 实时通信 | [gRPC](https://grpc.io/) (grpcio) |
| 数据库 | [PostgreSQL](https://www.postgresql.org/) 18+ (psycopg + SQLAlchemy 2.0) |
| 缓存 / 会话 | [Redis](https://redis.io/) 7+ (hiredis) |
| 协议定义 | [Protocol Buffers 3](https://protobuf.dev/) |
| 包管理 | [uv](https://docs.astral.sh/uv/) |
| 密钥管理 | [PGPy](https://pgpy.readthedocs.io/) (OpenPGP) |

## 核心功能

### 多租户架构

- 基于子域名的行级租户隔离（如 `school-a.cims.example.com`）
- 每个租户拥有独立数据空间，通过 `tenant_id` 字段关联所有业务数据
- 支持租户级 API Key 分发与轮换
- Redis 缓存租户解析结果，降低数据库压力

### 三端口服务

| 端口 | 服务 | 说明 |
|------|------|------|
| `:50050` | **Client API** | 面向 ClassIsland 客户端 — 提供配置清单（Manifest）和资源文件下载 |
| `:50051` | **Admin API** | 管理后台 — 租户 CRUD、配置文件管理、批量操作、指令下发 |
| `:50052` | **gRPC** | Cyrene_MSP 协议 — 客户端注册、握手、命令推送、配置上传、审计 |

### 上游 Cyrene_MSP 协议兼容性

| 服务 | 状态 | 说明 |
|------|------|------|
| `ClientRegister` | ✅ 已实现 | 客户端注册 + PGP 密钥交换 |
| `Handshake` | ✅ 已实现 | 双向握手认证 + 会话建立 |
| `ClientCommandDeliver` | ✅ 已实现 | 双向流式命令推送（Ping/Pong 心跳） |
| `ConfigUpload` | ✅ 已实现 | 客户端配置上传到服务端 |
| `Audit` | ✅ 已实现 | 审计事件上报与持久化 |

### 管理功能

- **配置文件 CRUD**：课表（ClassPlan）、时间表（TimeLayout）、科目（Subject）等全量管理
- **批量操作**：支持批量创建、更新、删除配置文件
- **指令下发**：通知推送、远程重启、获取客户端配置
- **客户端状态**：在线/离线状态查询（基于 gRPC 会话）
- **资源令牌**：一次性 / 多次使用的安全下载令牌

## 快速开始

### 先决条件

- [Python 3.10+](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/) 包管理器
- PostgreSQL 18+
- Redis 7+

### 安装与运行

```bash
# 1. 克隆仓库
git clone https://github.com/MINIOpenSource/CIMS-backend.git
cd CIMS-backend

# 2. 复制环境变量模板（按需修改）
cp .env.example .env

# 3. 安装依赖
uv sync --all-groups

# 4. 启动服务
uv run cims
```

首次启动会自动在 PostgreSQL 中创建所有数据表。

> 💡 详细的开发环境搭建（含 Docker 基础设施）请参阅 [DEVELOPMENT.md](DEVELOPMENT.md)。

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | `postgresql+psycopg://postgresql:password@localhost:5432/cims` | PostgreSQL 连接串 |
| `REDIS_URL` | `redis://:password@localhost:6379/0` | Redis 连接串 |
| `CIMS_BASE_DOMAIN` | `localhost` | 多租户基础域名 |
| `CIMS_ADMIN_SECRET` | `change-me` | 超级管理员认证密钥 |
| `CIMS_CLIENT_PORT` | `50050` | Client API 端口 |
| `CIMS_ADMIN_PORT` | `50051` | Admin API 端口 |
| `CIMS_GRPC_PORT` | `50052` | gRPC 服务端口 |
| `CIMS_KEY_FILE` | `cims_server.key` | PGP 服务器密钥文件路径 |

## 项目结构

```
CIMS-backend/
├── api/Protobuf/                   # Proto 源文件（Cyrene_MSP 协议定义）
│   ├── AuditEvent/                 #   审计事件消息
│   ├── Client/                     #   客户端请求消息
│   ├── Command/                    #   命令类型定义
│   ├── Enum/                       #   枚举定义
│   ├── Server/                     #   服务端响应消息
│   └── Service/                    #   gRPC 服务接口
├── app/
│   ├── api/                        # FastAPI 路由层
│   │   ├── admin/                  #   租户管理路由（CRUD / Token / Auth）
│   │   ├── client/                 #   客户端 Manifest & 资源下载
│   │   ├── command/                #   指令下发 & 配置文件管理
│   │   ├── management_config/      #   ManagementServer.json 生成
│   │   └── schemas/                #   请求 / 响应 Pydantic 模型
│   ├── apps/                       # FastAPI Sub-Application 工厂
│   │   ├── admin_app.py            #   Admin API 应用
│   │   ├── client_app.py           #   Client API 应用
│   │   └── lifespan.py             #   生命周期管理（DB / Redis / gRPC）
│   ├── core/                       # 核心基础设施
│   │   ├── auth/                   #   认证（Bearer Token / gRPC Interceptor）
│   │   ├── config.py               #   全局配置（环境变量绑定）
│   │   ├── redis/                  #   Redis 连接池 & 访问器
│   │   └── tenant/                 #   租户上下文解析 & 缓存
│   ├── grpc/                       # gRPC 服务层
│   │   ├── api/Protobuf/           #   生成的 protobuf Python 代码 & 类型存根
│   │   ├── server/                 #   五个 Cyrene_MSP 服务实现
│   │   └── session/                #   会话管理（状态机 / 密钥 / 在线状态）
│   ├── models/                     # SQLAlchemy ORM 模型
│   │   ├── domain/                 #   领域模型（课表、时间表、科目等）
│   │   ├── database.py             #   异步引擎 & Session 工厂
│   │   └── ...                     #   租户、客户端、审计等模型
│   ├── services/                   # 业务逻辑层
│   │   ├── auth_token/             #   认证令牌（生成 / 验证 / 吊销）
│   │   └── resource_token/         #   资源下载令牌（创建 / 解析）
│   └── main.py                     # 入口 — 三端口并行启动
├── tests/                          # pytest 测试套件
├── .env.example                    # 环境变量模板
├── .github/workflows/              # CI 流水线
├── pyproject.toml                  # 项目元数据 & 依赖声明
└── uv.lock                         # 依赖锁定文件
```

## API 文档

详见 [APIDocument.md](APIDocument.md)，涵盖所有 HTTP 端点与 gRPC 服务的请求/响应格式。

## 开发

详见 [DEVELOPMENT.md](DEVELOPMENT.md)，包含：

- Docker 基础设施搭建
- 依赖安装与开发服务器启动
- Protobuf 代码生成
- 测试与覆盖率
- IDE 配置推荐

## 贡献

详见 [CONTRIBUTING.md](CONTRIBUTING.md)，包含：

- 贡献流程与 Pull Request 规范
- 多租户开发注意事项
- 代码规范与提交约定

## 许可证

本项目基于 [GPL-3.0](LICENSE) 协议开源。

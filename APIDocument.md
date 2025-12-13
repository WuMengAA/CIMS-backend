# ClassIsland 集控与客户端 API 及配置文件文档

本文档旨在说明 ClassIsland 客户端与其集控后端（CIMS-backend）之间的 API 交互，以及相关的配置文件结构。

## 概述

ClassIsland 客户端通过 HTTP API 从集控后端获取配置清单（Manifest）和具体的配置文件。集控后端同时提供 gRPC 服务用于客户端注册和实时指令下发。

## 1. 客户端 API (供 ClassIsland 客户端实例使用)

### 1.1 获取客户端配置清单 (Manifest)

客户端首先请求此接口以获取其专属的配置资源清单。

*   **Endpoint**: `GET /api/v1/client/{client_uid}/manifest`
*   **Path Parameters**:
    *   `client_uid` (string, 必选): 客户端的唯一标识符 (UUID)。
*   **Query Parameters**:
    *   `version` (integer, 可选): 客户端当前配置的版本号（通常是时间戳）。服务器用此判断是否需要更新。如果未提供，服务器通常会返回最新的配置。
*   **请求示例**:
    `GET /api/v1/client/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/manifest?version=1678886400`
*   **响应格式**: `application/json`
*   **响应成功 (200 OK)**:
    ```json
    {
        "ClassPlanSource": { // 课表源信息
            "Value": "/api/v1/client/ClassPlan?name=default_classplan", // 获取课表的URL路径
            "Version": 1678886401 // 课表版本
        },
        "TimeLayoutSource": { // 时间表源信息
            "Value": "/api/v1/client/TimeLayout?name=default_timelayout",
            "Version": 1678886402
        },
        "SubjectsSource": { // 科目源信息
            "Value": "/api/v1/client/Subjects?name=default_subjects",
            "Version": 1678886403
        },
        "DefaultSettingsSource": { // 默认客户端设置源信息
            "Value": "/api/v1/client/DefaultSettings?name=default_settings",
            "Version": 1678886404
        },
        "PolicySource": { // 策略源信息
            "Value": "/api/v1/client/Policy?name=default_policy",
            "Version": 1678886405
        },
        "ServerKind": 0, // 服务器类型 (0: Serverless, 1: ManagementServer)
        "OrganizationName": "我的学校" // 组织名称
    }
    ```
    *   `Value` 字段中的 URL 是相对于服务器 API Host 的路径。客户端需要将服务器的 Host 和 Port （以及可能的 http/https 前缀）与此路径拼接。
    *   如果 `profile_config` 中未找到 `client_uid` 对应的配置，则会使用默认的资源名称（如 `default_classplan`）。

### 1.2 获取具体配置文件

客户端根据 Manifest 中获取到的 URL 来请求具体的配置文件。

*   **Endpoint**: `GET /api/v1/client/{resource_type}`
*   **Path Parameters**:
    *   `resource_type` (string, 必选): 资源类型，例如 `ClassPlan`, `TimeLayout`, `Subjects`, `DefaultSettings`, `Policy`。
*   **Query Parameters**:
    *   `name` (string, 必选): 资源文件的名称 (不含扩展名)，例如 `default_classplan`。
*   **请求示例**:
    `GET /api/v1/client/ClassPlan?name=default_classplan`
*   **响应格式**: `application/json`
*   **响应成功 (200 OK)**:
    响应体是对应资源类型的 JSON 内容。
    例如，请求 `/api/v1/client/Policy?name=default_policy` 会返回 `ManagementPolicy` 结构的 JSON。
*   **响应失败**:
    *   `404 Not Found`: 如果请求的资源不存在。

## 2. 命令 API (供服务器管理使用)

这些 API 用于服务器的内部管理和维护。

### 2.1 配置文件管理 (`/command/datas/{resource_type}/...`)

*   `resource_type` 可以是: `ClassPlan`, `DefaultSettings`, `Policy`, `Subjects`, `TimeLayout`。

    *   **创建配置文件**: `GET /command/datas/{resource_type}/create?name=<filename>`
        *   创建一个新的空配置文件。
        *   响应: JSON `{"status": "success/error", "message": "..."}`

    *   **删除配置文件**: `DELETE /command/datas/{resource_type}/delete?name=<filename>` (也支持GET)
        *   删除指定的配置文件。
        *   响应: JSON `{"status": "success/error", "message": "..."}`

    *   **列出配置文件**: `GET /command/datas/{resource_type}/list`
        *   列出指定资源类型下的所有配置文件名。
        *   响应: JSON `["filename1", "filename2", ...]`

    *   **写入配置文件**: `PUT /command/datas/{resource_type}/write?name=<filename>` (也支持POST)
        *   **Request Body**: 对应资源类型的 JSON 内容。
        *   响应: JSON `{"status": "success/error", "message": "..."}`

### 2.2 客户端管理 (`/command/clients/...`)

    *   **列出已注册客户端**: `GET /command/clients/list`
        *   响应: JSON `["client_uid_1", "client_uid_2", ...]`

    *   **获取客户端状态**: `GET /command/clients/status`
        *   响应: JSON 列表，每个对象包含:
            ```json
            [
              {
                "uid": "client_uid_1",
                "name": "client_id_1",
                "status": "online/offline",
                "lastHeartbeat": "YYYY-MM-DDTHH:MM:SS.ffffffZ", // ISO 8601 格式, UTC
                "ip": "client_ip_address"
              }
            ]
            ```

    *   **获取单个客户端详情**: `GET /command/client/{client_uid}/details`
        *   响应: JSON 对象，合并 `/status` 的信息与配置信息。

### 2.3 指令下发 (`/command/client/{client_uid}/...`)

    *   **重启客户端应用**: `GET /command/client/{client_uid}/restart`
        *   通过 gRPC 向客户端发送 `RestartApp` 指令。
        *   响应: JSON `{"status": "success/error", "message": "..."}`

    *   **通知客户端更新数据**: `GET /command/client/{client_uid}/update_data`
        *   通过 gRPC 向客户端发送 `DataUpdated` 指令。
        *   响应: JSON `{"status": "success/error", "message": "..."}`

    *   **发送通知到客户端**: `POST /command/client/{client_uid}/send_notification`
        *   通过 gRPC 向客户端发送 `SendNotification` 指令。
        *   响应: JSON `{"status": "success/error", "message": "..."}`

## 3. gRPC API

由 `api/Protobuf/` 目录下的 `.proto` 文件定义。

### 3.1 Service: `ClientRegister`

    *   **RPC: `Register`**
        *   **Request**: `ClientRegisterCsReq`
        *   **Response**: `ClientRegisterScRsp`
        *   **逻辑**: 注册或更新客户端信息。

    *   **RPC: `UnRegister`**
        *   **Request**: `ClientRegisterCsReq`
        *   **Response**: `ClientRegisterScRsp`
        *   **逻辑**: 注销客户端。

### 3.2 Service: `ClientCommandDeliver`

    *   **RPC: `ListenCommand`** (双向流)
        *   客户端通过 gRPC Metadata 发送 `cuid` (客户端UID)。
        *   双向流用于维持连接、心跳 (Ping/Pong) 和服务器向客户端下发指令。

## 4. 配置文件结构说明

所有配置文件内容均为 JSON 格式，存储在数据库中。
结构与 ClassIsland 客户端模型一致。

*   **服务器设置**: 组织名称等。
*   **客户端注册信息**: ID, Name, Status 等。
*   **客户端配置映射**: 定义每个客户端使用哪些资源。
*   **资源类型**: `ClassPlan` (课表), `TimeLayout` (时间表), `Subjects` (科目), `DefaultSettings` (默认设置), `Policy` (策略)。

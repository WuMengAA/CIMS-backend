# CIMS API 文档

## 概述

CIMS 提供四个独立端口的 API 服务：

| 端口 | 名称 | 用途 |
|------|------|------|
| `27041` | Client API | ClassIsland 客户端获取配置和资源 |
| `27042` | Management API | 用户认证、账户管理、资源管理、客户端控制 |
| `27043` | Admin API | 超级管理员全局用户/账户/系统管理 |
| `27044` | gRPC | Cyrene_MSP 协议（注册、命令推送、心跳） |

---

## Client API `:27041`

### `GET /`

服务状态检测。

**响应**

```json
{"message": "CIMS Client API 运行中"}
```

### `GET /api/v1/client/{client_uid}/manifest`

获取客户端配置清单。

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| `client_uid` | path | string | ✅ | 客户端唯一标识 |

**响应** — Manifest JSON，包含各资源类型的名称列表。

### `GET /api/v1/client/{resource_type}`

获取指定资源（302 重定向到令牌下载地址）。

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| `resource_type` | path | string | ✅ | 合法值: `ClassPlan`, `TimeLayout`, `Subjects`, `Policy`, `DefaultSettings`, `Components`, `Credentials` |
| `name` | query | string | ✅ | 资源文件名 |

### `GET /get`

通过令牌获取资源 JSON 内容。

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| `token` | query | string | ✅ | 一次性资源访问令牌 |

**响应** — 资源 JSON 内容。

### `GET /api/v1/management-config`

获取 ManagementPreset 引导配置。

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| `class_identity` | query | string | ❌ | 班级标识（匹配预注册客户端） |

**响应**

```json
{
  "IsManagementEnabled": true,
  "ManagementServerKind": 1,
  "ManagementServer": "https://{slug}.example.com",
  "ManagementServerGrpc": "grpc://{slug}.example.com",
  "ClassIdentity": "",
  "ManifestUrlTemplate": ""
}
```

---

## Management API `:27042`

> 所有端点（除 `/user/apply` 和 `/user/auth`）需要 `Authorization: Bearer {token}` 请求头。

### Token 管理

#### `POST /token/refresh`

刷新当前会话令牌。

**请求头** — `Authorization: Bearer {token}`

**响应**

```json
{"token": "新的会话令牌"}
```

#### `POST /token/verify`

验证令牌有效性。

**请求头** — `Authorization: Bearer {token}`

**响应**

```json
{"valid": true, "user_id": "uuid"}
```

#### `POST /token/deactivate`

注销当前令牌（登出）。

**请求头** — `Authorization: Bearer {token}`

**响应**

```json
{"status": "success", "message": "已登出"}
```

### 用户

#### `POST /user/apply`

申请注册新用户。注册后进入 Pending 状态，需管理员审核。用户名可选，留空自动生成。

**请求体**

```json
{
  "email": "user@example.com",
  "password": "至少12位密码",
  "username": "可选，留空自动生成",
  "display_name": "显示名（可选）"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `email` | string (email) | ✅ | 用户邮箱 |
| `password` | string | ✅ | 12~128 位密码 |
| `username` | string | ❌ | 用户名，留空自动 `user_xxxx` |
| `display_name` | string | ❌ | 显示名称，默认空 |

**响应**

```json
{"status": "success", "message": "注册成功，等待管理员审核"}
```

#### `POST /user/auth`

用户登录，获取会话令牌。

**请求体**

```json
{
  "email": "user@example.com",
  "password": "密码"
}
```

**响应（正常登录）**

```json
{"token": "会话令牌"}
```

**响应（需要 2FA）**

```json
{"requires_2fa": true, "temp_token": "临时令牌"}
```

#### `GET /user/info`

获取当前用户信息。

**响应**

```json
{
  "id": "uuid",
  "username": "user_a1b2c3d4",
  "email": "user@example.com",
  "display_name": "张三",
  "role_code": "normal",
  "is_active": true,
  "can_create_account": false,
  "created_at": "2026-01-01T00:00:00Z"
}
```

#### `POST /user/info/email`

修改邮箱。

**请求体**

```json
{"email": "new@example.com"}
```

#### `POST /user/info/username`

修改用户名。

**请求体**

```json
{"username": "new_username"}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `username` | string | 3~64 位，字母数字下划线 |

#### `POST /user/info/password/change`

修改密码（需旧密码）。

**请求体**

```json
{
  "old_password": "旧密码",
  "new_password": "至少12位新密码"
}
```

### 2FA (TOTP)

#### `POST /user/2fa/totp/enable`

启用 TOTP。

**响应**

```json
{
  "secret": "BASE32密钥",
  "uri": "otpauth://totp/...",
  "recovery_codes": ["code1", "code2", "..."]
}
```

#### `POST /user/2fa/totp/confirm`

确认绑定（提交首次 TOTP 码）。

**请求体**

```json
{"code": "123456"}
```

#### `POST /user/2fa/totp/disable`

禁用 TOTP。

**请求体**

```json
{"password": "当前密码"}
```

#### `POST /user/2fa/totp/verify`

登录时验证 TOTP。

**请求体**

```json
{"temp_token": "临时令牌", "code": "123456"}
```

**响应**

```json
{"token": "正式会话令牌"}
```

#### `POST /user/2fa/totp/recover`

使用恢复码登录。

**请求体**

```json
{"temp_token": "临时令牌", "recovery_code": "恢复码"}
```

### 账户管理

#### `POST /account/list`

列出当前用户有权访问的所有账户。

**响应** — `AccountOut[]`

```json
[
  {
    "id": "uuid",
    "name": "学校名称",
    "slug": "org-a1b2c3d4",
    "api_key": "...",
    "is_active": true,
    "created_at": "2026-01-01T00:00:00Z"
  }
]
```

#### `POST /account/search?q={keyword}`

搜索账户。

| 参数 | 位置 | 类型 | 说明 |
|------|------|------|------|
| `q` | query | string | 搜索关键字 |

#### `POST /account/apply`

申请创建新账户。需 `can_create_account` 权限。Slug 可选，留空自动生成。

**请求体**

```json
{"name": "新学校名称", "slug": "可选，留空自动生成"}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 账户名称 |
| `slug` | string | ❌ | 3~64 位 slug，留空自动 `org-xxxx` |

**响应** — `AccountOut` (201)

#### `POST /account/{account_id}/delete`

停用账户。

#### `GET /account/{account_id}/info`

获取账户详情。

**响应** — `AccountOut`

#### `POST /account/{account_id}/info/slug`

修改账户 slug。

**请求体**

```json
{"slug": "new-slug-name"}
```

### 资源管理 `/account/{account_id}/{resource_type}/...`

#### `GET /{resource_type}/create?name={name}`

创建空资源文件。

#### `GET /{resource_type}/list`

列出所有资源文件名。

#### `GET /{resource_type}/delete?name={name}`

删除指定资源。

#### `GET /{resource_type}/token?name={name}`

签发资源访问令牌。

**响应**

```json
{"token": "一次性令牌", "url": "/get?token=..."}
```

#### `POST /{resource_type}/write?name={name}`

覆盖写入资源。

**请求体** — 资源 JSON 内容。

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| `name` | query | string | ✅ | 资源文件名 |
| `version` | query | int | ❌ | 乐观锁版本号 |

#### `PATCH /{resource_type}/update?name={name}`

增量合并更新资源。

**请求体** — 合并用 JSON 内容。

### 客户端管理 `/account/{account_id}/client/...`

#### `GET /clients/list`

列出已注册客户端 UID。

#### `GET /clients/status`

获取在线客户端状态。

#### `GET /client/{uid}/details`

查询客户端注册详情及在线状态。

**响应**

```json
{
  "uid": "client-uid",
  "name": "client-id",
  "mac": "AA:BB:CC:DD:EE:FF",
  "status": "online",
  "registered_at": "2026-01-01T00:00:00Z"
}
```

#### `GET /client/{uid}/restart`

重启客户端应用。

#### `GET /client/{uid}/update_data`

强制客户端同步最新数据。

#### `POST /client/{uid}/send_notification`

发送通知。

**请求体**

```json
{
  "title": "标题",
  "content": "内容",
  "icon": "info",
  "tts": false,
  "urgent": false
}
```

#### `GET /client/{uid}/get_config?config_type={type}`

请求客户端上报运行时配置。

### 配对码管理 `/account/{account_id}/pairing/...`

#### `POST /list`

列出配对码。

#### `POST /{pairing_id}/approve`

批准配对码。

#### `POST /{pairing_id}/reject`

拒绝配对码。

### 预注册客户端 `/account/{account_id}/pre-registration/...`

#### `POST /list`

列出预注册客户端。

#### `GET /{pre_reg_id}`

获取预注册客户端信息。

#### `POST /{pre_reg_id}/delete`

删除预注册客户端。

#### `GET /{pre_reg_id}/ManagementPreset.json`

下载引导配置。

### 访问控制 `/account/{account_id}/access/...`

#### `POST /list`

列出具权用户。

### 邀请 `/account/{account_id}/invitation/...`

#### `POST /list`

列出邀请。

#### `POST /create`

创建邀请。

### 批量操作

#### `POST /account/bulk`

执行批量资源操作。

**请求体**

```json
{
  "operations": [
    {
      "action": "write",
      "resource_type": "ClassPlan",
      "name": "文件名",
      "payload": {}
    }
  ]
}
```

| action | 说明 |
|--------|------|
| `create` | 创建资源 |
| `write` | 覆盖写入 |
| `update` | 增量合并 |
| `delete` | 删除资源 |

---

## Admin API `:27043`

> 所有端点需要超级管理员认证（`Authorization: Bearer {admin_secret}`）。

### 用户管理

#### `POST /user/list?offset=0&limit=20`

分页查询所有用户。

**响应** — `UserOut[]`

#### `POST /user/search?q={keyword}`

搜索用户。

#### `POST /user/create`

直接创建用户（跳过审核）。用户名可选，留空自动生成。

**请求体**

```json
{
  "email": "user@example.com",
  "password": "至少12位密码",
  "username": "可选",
  "display_name": "可选"
}
```

**响应** — `UserOut`

#### `GET /user/{user_id}`

获取用户信息。

**响应** — `UserOut`

#### `POST /user/{user_id}`

修改用户信息。

**请求体**

```json
{
  "display_name": "新名称",
  "role_code": "normal",
  "is_active": true,
  "can_create_account": true
}
```

#### `POST /user/{user_id}/delete`

删除用户。

#### `POST /user/{user_id}/password/reset`

重置用户密码（无需旧密码）。

**请求体**

```json
{"new_password": "至少12位新密码"}
```

### 用户 2FA 管理

#### `POST /user/{user_id}/2fa/enable`

为用户启用 TOTP。

#### `POST /user/{user_id}/2fa/disable`

禁用用户 TOTP。

#### `POST /user/{user_id}/2fa/reset`

重置用户 TOTP 密钥。

### 用户审核

#### `POST /user/pending/list?offset=0&limit=50`

列出待审核用户。

#### `POST /user/pending/approve/{user_id}`

批准用户注册。

#### `POST /user/pending/reject/{user_id}`

拒绝用户注册。

### 账户管理

#### `GET /account`

列出所有账户（跨租户）。

**响应** — `AccountOut[]`

### 系统设置

#### `GET /settings`

获取所有系统设置。

**响应** — 键值对 JSON。

#### `POST /settings`

修改系统设置。

**请求体** — 键值对 JSON。

```json
{"key1": "value1", "key2": "value2"}
```

### 批量操作

#### `POST /bulk`

执行批量资源操作（同 Management API `/account/bulk`）。

---

## gRPC `:27044`

### `ClientRegister`

客户端注册。

**请求** — `ClientRegisterCsReq`

| 字段 | 类型 | 说明 |
|------|------|------|
| `uid` | string | 客户端唯一标识 |
| `client_id` | string | 客户端 ID |
| `mac` | string | MAC 地址 |
| `ip` | string | IP 地址 |
| `pairing_code` | string | 配对码 |

**响应** — `ClientRegisterScRsp`

| 字段 | 类型 | 说明 |
|------|------|------|
| `RetCode` | enum | 返回码（Success/Fail） |
| `ServerPublicKey` | bytes | 服务器公钥 |

### `ClientCommand` (双向流)

命令通道。

**客户端发送** — `ClientCommandDeliverCsReq`（命令响应 / Ping）

**服务端推送** — `ClientCommandDeliverScRsp`

| 字段 | 类型 | 说明 |
|------|------|------|
| `RetCode` | enum | 返回码 |
| `Type` | enum | 命令类型 (`RestartApp`, `DataUpdated`, `SendNotification`, `GetClientConfig`) |
| `Payload` | bytes | Protobuf 序列化的命令负载 |

### `HeartBeat`

心跳保活。客户端定期发送心跳，服务端回复确认。

---

## 通用数据模型

### UserOut

```json
{
  "id": "uuid",
  "username": "user_a1b2c3d4",
  "email": "user@example.com",
  "display_name": "显示名称",
  "role_code": "normal",
  "is_active": true,
  "can_create_account": false,
  "created_at": "2026-01-01T00:00:00Z"
}
```

### AccountOut

```json
{
  "id": "uuid",
  "name": "账户名称",
  "slug": "org-a1b2c3d4",
  "api_key": "API密钥",
  "is_active": true,
  "created_at": "2026-01-01T00:00:00Z"
}
```

### StatusResponse

```json
{
  "status": "success|error",
  "message": "操作结果描述"
}
```

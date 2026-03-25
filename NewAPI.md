:27041 Client API
  <GET> 服务状态检测
  /api/v1/client
    /{client_uid}/manifest 获取客户端清单
    /{resource_type} 获取客户端资源
  /get 令牌换取资源内容
  /api/v1/management-config 获取引导配置

:27042 Management API
  <GET> 服务状态检测
  /token
    /refresh 刷新 Token
    /verify 验证 Token
    /deactivate 登出
  /user
    /apply 申请注册
    /auth 请求 Token (登录)
    /info 获取用户信息
    /2fa
      /totp
        /enable 启用 TOTP
        /confirm 确认绑定 TOTP
        /disable 禁用 TOTP
        /verify 验证 TOTP
        /recover 恢复码登录
    /info
      <GET> 获取用户信息
      /email 修改邮箱
      /username 修改用户名
      /password
        /reset 重置密码
        /change 修改密码
  /account
    /list 列出所有账户
    /search 搜索账户
    /apply 申请创建新账户
    /{account_id}
      /delete 删除账户
      /info
        <GET> 获取账户信息
        /slug 修改账户 slug
      /{resource_type}
        /list 列出资源
        /search 搜索资源
        /create 创建资源
        /upload 上传资源
        /{resource_id}
          /delete 删除资源
          /rename 重命名资源
          <POST> 覆盖写入资源
          <GET> 下载资源
      /client
        /list 列出客户端
        /search 搜索客户端
        /{client_id}
          /delete 删除客户端
          /rename 重命名客户端
          /status 获取客户端状态
          <GET> 客户端详情
          /disconnect 断开连接
          /disable 禁用客户端
          /enable 启用客户端
          /config 修改客户端使用的档案组
          /command
            /restart 重启客户端
            /update-data 强制同步数据
            /send-notification 发送通知
            /get-config 获取运行时配置
      /pairing
        /list 列出配对码
        /search 搜索配对码
        /{pairing_id}
          /reject 拒绝配对码
          /approve 批准配对码
        /enable 启用配对码
        /disable 禁用配对码
      /pre-registration
        /list 列出预注册客户端
        /search 搜索预注册客户端
        /{pre_reg_id}
          /delete 删除预注册客户端
          /rename 重命名预注册客户端
          <GET> 获取预注册客户端信息
          /enable 启用预注册客户端
          /disable 禁用预注册客户端
          /ManagementPreset.json 下载引导配置
          /config 修改预注册客户端使用的档案组
      /access
        /list 列出具权用户
        /search 搜索具权用户
        /{user_id}
          /delete 删除具权用户
          /rename 重命名具权用户
          <GET> 获取具权用户信息
          <POST> 修改具权用户的权限
      /invitation
        /list 列出邀请列表
        /create 创建邀请
        /search 搜索邀请
        /{invitation_id}
          /delete 删除邀请
          /rename 重命名邀请
          <GET> 获取邀请信息
    /bulk
      <POST> 批量操作

:27043 Admin API
  / 服务状态检测
  /user
    /list 列出所有用户
    /search 搜索用户
    /create 创建用户
    /{user_id}
      /delete 删除用户
      /rename 重命名用户
      <GET> 获取用户信息
      <POST> 修改用户信息
      /password
        /reset 重置密码
        /change 修改密码
      /2fa
        /enable 启用 TOTP
        /disable 禁用 TOTP
        /verify 验证 TOTP
        /reset 重置 TOTP
    /pending
      /list 列出待审核用户
      /approve/{user_id} 批准用户
      /reject/{user_id} 拒绝用户
  /account
    : 复用 Management API 的 /account 接口，但具备所有权限
    : 允许 ?role={user_id} 以某个用户身份操作
  /settings
    <GET> 获取系统设置
    <POST> 修改系统设置
  /bulk
    <POST> 批量操作
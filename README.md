# Noteford 开源版 Skill

让支持本机工具调用的 AI 连接 **Noteford 开源版（Community）**，检索本人已授权的微信聊天与素材。

```sh
npx skills add Followhongyun/noteford-community-skill --skill noteford-community
```

也可以下载本仓库 ZIP，解压后将整个 Skill 文件夹交给支持本地 Skill 的客户端安装。应用需单独从提供者获取；本仓库不包含应用源码、安装包、聊天资料或凭据。

先打开正式 Community 安装版，再让 AI 按 [接入说明](references/connection.md) 注册 MCP、由本人在应用中确认授权，并实际调用 `list_libraries`、`get_status` 验证。安装文件不等于授权；当前对话未加载工具时，按客户端支持方式刷新或新开对话。

需要 Node.js/npm；Mac 注册脚本需要 Python 3。自编译且更换签名身份的应用需要对应调整信任校验，不能冒充官方安装版。此 Skill 不自动切换到会员版；会员版的现有 Skill 入口不变。

来源：Noteford Community 0.1.1 源码快照（2026-11-09）。采用 AGPL-3.0-only，见 LICENSE。

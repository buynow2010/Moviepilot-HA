# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2025-10-11

### 🔧 变更

- 移除以下实体：
  - 传感器：`下载通知`、`整理通知`
  - 二进制传感器：`有任务运行`
- 更新文档与翻译以反映上述变更。

### ⚠️ 兼容性

- 这是一次破坏性变更（移除实体）。如果你在自动化或仪表盘中使用了这些实体，请相应调整配置。
- 替代方案：仍可使用 Webhook 推送或事件总线 `moviepilot_notification` 接收来自 MoviePilot 的通知。

**完整变更**: https://github.com/buynow2010/Moviepilot-HA/commits/v1.1.0

---

## [1.0.0] - 2025-10-08

### 🎉 首次发布

这是 MoviePilot Home Assistant 集成的首个正式版本，提供完整的 MoviePilot 监控和双向通知功能。

### ✨ 新增功能

#### 核心功能
- ✅ 完整的 MoviePilot 服务监控
- ✅ 12 个状态传感器
- ✅ 3 个二进制传感器
- ✅ 双向通知支持

#### 传感器

**系统监控（4个）**
- CPU 使用率 (`sensor.moviepilot_cpu_usage`)
- 内存使用率 (`sensor.moviepilot_memory_usage`)
- 磁盘使用率 (`sensor.moviepilot_disk_usage`)
- 磁盘剩余空间 (`sensor.moviepilot_disk_free`)

**下载器监控（1个）**
- 下载速度 (`sensor.moviepilot_download_speed`)

**任务管理（1个）**
- 运行中任务数 (`sensor.moviepilot_running_tasks`)

**媒体统计（4个）**
- 电影数量 (`sensor.moviepilot_movie_count`)
- 剧集数量 (`sensor.moviepilot_tv_count`)
- 剧集集数 (`sensor.moviepilot_episode_count`)
- 用户数量 (`sensor.moviepilot_user_count`)

**消息通知（2个）⭐ 特色功能**
- 下载通知 (`sensor.moviepilot_下载通知`) - 监控下载状态变化
- 整理通知 (`sensor.moviepilot_整理通知`) - 监控整理状态变化

**二进制传感器（3个）**
- 在线状态 (`binary_sensor.moviepilot_online`)
- 任务运行状态 (`binary_sensor.moviepilot_tasks_running`)
- 下载状态 (`binary_sensor.moviepilot_downloading`)

#### 通知功能

**发送通知到 MoviePilot**
- `notify.moviepilot` - 标准 Home Assistant notify 服务
- `moviepilot.send_notification` - 自定义服务
- 支持 4 种通知类型：Manual, System, Download, Transfer

**接收 MoviePilot 通知 ⭐ 特色功能**

方式 1: **Webhook 直推（推荐）**
- ✅ 零延迟实时推送
- ✅ 支持所有 MoviePilot 通知类型
- ✅ 完整通知内容
- ✅ 自动触发 `moviepilot_notification` 事件
- 📖 配置指南：[WEBHOOK_GUIDE.md](WEBHOOK_GUIDE.md)

方式 2: **状态监控（自动）**
- ✅ 零配置自动启用
- ✅ 自动监控下载/整理状态变化
- ✅ 触发 `moviepilot_notification` 事件
- ⚠️ 轻微延迟（0-30秒）

### 📚 文档

- ✅ [README.md](README.md) - 完整功能介绍和快速开始
- ✅ [INSTALL.md](INSTALL.md) - 详细安装指南
- ✅ [WEBHOOK_GUIDE.md](WEBHOOK_GUIDE.md) - Webhook 配置完整指南
- ✅ [RECEIVE_NOTIFICATIONS.md](RECEIVE_NOTIFICATIONS.md) - 通知接收详细指南（20+ 自动化示例）
- ✅ [NOTIFICATION_GUIDE.md](NOTIFICATION_GUIDE.md) - 通知发送详细指南
- ✅ [QUICK_START.md](QUICK_START.md) - 快速开始指南
- ✅ [TECHNICAL_DETAILS.md](TECHNICAL_DETAILS.md) - 技术实现细节
- ✅ [AUTOMATION_EXAMPLES.yaml](AUTOMATION_EXAMPLES.yaml) - 自动化配置示例集合
- ✅ [LICENSE](LICENSE) - MIT 开源许可证

### 🔧 技术实现

- 基于 MoviePilot API v1
- 完整的错误处理和日志记录
- 优化的并发请求
- 参数验证和自动降级
- 符合 Home Assistant 2024.1+ 标准
- 完全符合 HACS 集成规范

### 🎯 支持的功能

- ✅ 实时系统资源监控
- ✅ 下载任务监控
- ✅ 整理任务监控
- ✅ 媒体库统计
- ✅ 双向通知通信
- ✅ 事件驱动的通知系统
- ✅ 灵活的自动化集成
- ✅ Webhook 实时通知接收

### 🌟 亮点特性

1. **零配置通知接收** - 安装即用，自动监控 MoviePilot 状态变化
2. **Webhook 实时推送** - 零延迟接收所有 MoviePilot 通知
3. **丰富的自动化示例** - 提供 20+ 实用自动化配置
4. **完整的状态监控** - 15 个实体全方位监控
5. **双向通信** - HA ↔ MoviePilot 完美互通
6. **HACS 集成** - 一键安装，自动更新

### 🐛 已知问题

无

### 📝 注意事项

- 需要 Home Assistant 2024.1.0 或更高版本
- 需要 MoviePilot V2 或更高版本
- 需要有效的 MoviePilot API Token

### 🔗 链接

- **仓库**: https://github.com/buynow2010/Moviepilot-HA
- **问题反馈**: https://github.com/buynow2010/Moviepilot-HA/issues
- **讨论区**: https://github.com/buynow2010/Moviepilot-HA/discussions

### 🙏 致谢

感谢所有测试和反馈的用户！

---

**完整变更**: https://github.com/buynow2010/Moviepilot-HA/commits/v1.0.0

# MoviePilot Home Assistant 集成安装指南

## 📋 前置要求

在安装之前，请确保你已具备：

- ✅ **Home Assistant** 2024.1.0 或更高版本
- ✅ **MoviePilot** V2 或更高版本，并正常运行
- ✅ **MoviePilot API Token** - 从 MoviePilot 设置中获取

## 🚀 安装方法

### 方法 1: 通过 HACS 安装（推荐）

HACS（Home Assistant Community Store）是最简单的安装方式。

#### 步骤 1: 添加自定义仓库

1. 打开 Home Assistant
2. 点击侧边栏的 **HACS**
3. 点击 **集成 (Integrations)**
4. 点击右上角的 **⋮** 菜单
5. 选择 **自定义存储库 (Custom repositories)**
6. 在弹出的对话框中：
   - **存储库 URL**: `https://github.com/buynow2010/Moviepilot-HA`
   - **类别**: 选择 `Integration`
7. 点击 **添加 (Add)**

#### 步骤 2: 安装集成

1. 在 HACS 集成页面搜索框中输入 **MoviePilot**
2. 点击搜索结果中的 **MoviePilot**
3. 点击右下角的 **下载 (Download)** 按钮
4. 选择最新版本
5. 点击 **下载 (Download)** 确认

#### 步骤 3: 重启 Home Assistant

1. 进入 **配置** → **系统**
2. 点击 **重新启动**
3. 等待 Home Assistant 重启完成

### 方法 2: 手动安装

如果你不使用 HACS，可以手动安装。

#### 步骤 1: 下载集成文件

1. 访问 [GitHub Releases](https://github.com/buynow2010/Moviepilot-HA/releases)
2. 下载最新版本的 `moviepilot.zip`
3. 解压下载的文件

#### 步骤 2: 复制文件

1. 通过 SSH 或文件管理器访问 Home Assistant
2. 导航到 Home Assistant 配置目录（通常是 `/config`）
3. 如果不存在 `custom_components` 文件夹，创建它
4. 将解压后的 `moviepilot` 文件夹复制到 `custom_components/` 目录

最终目录结构应该是：
```
/config/
  └── custom_components/
      └── moviepilot/
          ├── __init__.py
          ├── api.py
          ├── binary_sensor.py
          ├── config_flow.py
          ├── const.py
          ├── manifest.json
          ├── notify.py
          ├── sensor.py
          ├── services.yaml
          ├── strings.json
          └── translations/
              └── zh-Hans.json
```

#### 步骤 3: 重启 Home Assistant

重启 Home Assistant 以加载新集成。

## ⚙️ 配置集成

安装并重启后，需要配置 MoviePilot 集成。

### 步骤 1: 获取 MoviePilot API Token

1. 登录 **MoviePilot Web 界面**
2. 进入 **设置 (Settings)**
3. 找到 **API** 或 **接口** 部分
4. 复制 **API Token**（如果没有，点击生成）

### 步骤 2: 添加集成

1. 在 Home Assistant 中，进入 **配置** → **设备与服务**
2. 点击右下角的 **+ 添加集成**
3. 在搜索框中输入 **MoviePilot**
4. 点击搜索结果中的 **MoviePilot**

### 步骤 3: 填写配置信息

在配置对话框中输入以下信息：

| 字段 | 说明 | 示例 |
|------|------|------|
| **主机地址 (Host)** | MoviePilot 服务器地址 | `ecorehome.cn` 或 `192.168.1.100` |
| **端口 (Port)** | MoviePilot 端口号 | `3000` (默认) |
| **API Token** | 从 MoviePilot 复制的 Token | `kxS5kZ_EOD2XKZ5K5lvfWw` |

### 步骤 4: 完成配置

1. 点击 **提交 (Submit)**
2. 等待连接测试完成
3. 如果配置正确，会显示 **成功 (Success)** 消息
4. 集成会自动创建所有实体

## ✅ 验证安装

### 检查实体

安装成功后，你应该能看到以下实体：

#### 传感器 (12 个)
- `sensor.moviepilot_cpu_usage` - CPU 使用率
- `sensor.moviepilot_memory_usage` - 内存使用率
- `sensor.moviepilot_disk_usage` - 磁盘使用率
- `sensor.moviepilot_disk_free` - 磁盘剩余空间
- `sensor.moviepilot_download_speed` - 下载速度
- `sensor.moviepilot_running_tasks` - 运行中任务
- `sensor.moviepilot_movie_count` - 电影数量
- `sensor.moviepilot_tv_count` - 剧集数量
- `sensor.moviepilot_episode_count` - 剧集集数
- `sensor.moviepilot_user_count` - 用户数量
- `sensor.moviepilot_下载通知` - 下载通知 ⭐
- `sensor.moviepilot_整理通知` - 整理通知 ⭐

#### 二进制传感器 (3 个)
- `binary_sensor.moviepilot_online` - 在线状态
- `binary_sensor.moviepilot_tasks_running` - 任务运行状态
- `binary_sensor.moviepilot_downloading` - 下载状态

### 测试通知服务

#### 发送测试通知到 MoviePilot

1. 进入 **开发者工具** → **服务**
2. 选择服务: `notify.moviepilot`
3. 输入服务数据：
   ```yaml
   title: "测试通知"
   message: "Home Assistant 集成测试"
   data:
     type: "Manual"
   ```
4. 点击 **调用服务**
5. 检查 MoviePilot 是否收到通知

#### 接收 MoviePilot 通知

1. 添加自动化配置（见下方）
2. 在 MoviePilot 中启动下载任务
3. 观察 Home Assistant 是否收到通知

## 🔔 配置通知接收（重要）

要接收 MoviePilot 的通知，需要配置自动化。

### 基础配置

在 `configuration.yaml` 或 `automations.yaml` 中添加：

```yaml
automation:
  # 接收所有 MoviePilot 通知
  - alias: "MoviePilot 通知接收"
    description: "将 MoviePilot 通知显示在 Home Assistant"
    trigger:
      - platform: event
        event_type: moviepilot_notification
    action:
      # 显示持久通知
      - service: persistent_notification.create
        data:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}"
          notification_id: "moviepilot_{{ trigger.event.data.timestamp }}"
```

### 手机通知配置

如果配置了 Mobile App，可以将通知发送到手机：

```yaml
automation:
  - alias: "MoviePilot 通知发送到手机"
    trigger:
      - platform: event
        event_type: moviepilot_notification
    action:
      - service: notify.mobile_app  # 替换为你的 mobile app 服务名
        data:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}"
          data:
            group: "moviepilot"
```

### 更多配置示例

查看完整的通知配置指南：
- [通知接收指南](RECEIVE_NOTIFICATIONS.md) - 20+ 自动化示例
- [通知发送指南](NOTIFICATION_GUIDE.md) - HA 发送通知到 MoviePilot

## 🎨 添加到仪表板

### Lovelace 卡片示例

```yaml
type: entities
title: MoviePilot 监控
entities:
  - entity: binary_sensor.moviepilot_online
    name: 在线状态
  - entity: sensor.moviepilot_cpu_usage
    name: CPU 使用率
  - entity: sensor.moviepilot_memory_usage
    name: 内存使用率
  - entity: sensor.moviepilot_disk_usage
    name: 磁盘使用率
  - entity: sensor.moviepilot_download_speed
    name: 下载速度
  - entity: sensor.moviepilot_running_tasks
    name: 运行任务
  - type: divider
  - entity: sensor.moviepilot_movie_count
    name: 电影
  - entity: sensor.moviepilot_tv_count
    name: 剧集
  - type: divider
  - entity: sensor.moviepilot_下载通知
    name: 下载状态
  - entity: sensor.moviepilot_整理通知
    name: 整理状态
```

### 状态卡片

```yaml
type: glance
title: MoviePilot 快速状态
entities:
  - entity: binary_sensor.moviepilot_online
  - entity: binary_sensor.moviepilot_downloading
  - entity: binary_sensor.moviepilot_tasks_running
  - entity: sensor.moviepilot_cpu_usage
  - entity: sensor.moviepilot_disk_usage
```

## 🔧 高级配置

### 自定义扫描间隔

默认每 30 秒更新一次数据。如需修改：

1. 在集成配置中点击 **选项 (Options)**
2. 修改 **扫描间隔 (Scan Interval)** (10-300 秒)
3. 点击 **提交**

### 启用调试日志

如需排查问题，可启用调试日志：

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.moviepilot: debug
    custom_components.moviepilot.api: debug
    custom_components.moviepilot.sensor: debug
    custom_components.moviepilot.notify: debug
```

## 🔄 更新集成

### 通过 HACS 更新

1. 打开 **HACS** → **集成**
2. 找到 **MoviePilot**
3. 如有新版本，会显示 **更新可用**
4. 点击 **更新**
5. 重启 Home Assistant

### 手动更新

1. 下载最新版本
2. 替换 `custom_components/moviepilot/` 文件夹
3. 重启 Home Assistant

## ❌ 卸载集成

如需卸载：

1. 进入 **配置** → **设备与服务**
2. 找到 **MoviePilot** 集成
3. 点击 **⋮** 菜单
4. 选择 **删除 (Delete)**
5. 确认删除

要完全移除文件：
- HACS 安装：在 HACS 中删除
- 手动安装：删除 `custom_components/moviepilot/` 文件夹

## 🐛 故障排查

### 无法连接

**问题**: 配置时提示"无法连接"

**解决方案**:
1. 检查 MoviePilot 服务是否运行
2. 确认主机地址和端口正确
3. 测试网络连接: `ping your_moviepilot_host`
4. 检查防火墙设置

### 认证失败

**问题**: 提示"认证失败"

**解决方案**:
1. 确认 API Token 正确
2. 在 MoviePilot 中重新生成 Token
3. 检查 Token 是否包含空格

### 实体不更新

**问题**: 传感器显示"不可用"

**解决方案**:
1. 检查 `binary_sensor.moviepilot_online` 状态
2. 查看 Home Assistant 日志
3. 重新加载集成

### 没有收到通知

**问题**: MoviePilot 通知未在 HA 中显示

**解决方案**:
1. 确认已配置通知接收自动化
2. 检查传感器状态: `sensor.moviepilot_下载通知`
3. 在开发者工具中监听 `moviepilot_notification` 事件
4. 查看日志中是否有事件触发记录

## 📞 获取帮助

如遇到问题：

1. 查看 [README](README.md)
2. 查看 [常见问题](https://github.com/buynow2010/Moviepilot-HA/issues)
3. 提交 [Issue](https://github.com/buynow2010/Moviepilot-HA/issues/new)

## 📚 相关文档

- [README](README.md) - 功能介绍
- [通知接收指南](RECEIVE_NOTIFICATIONS.md) - 详细的通知接收配置
- [通知发送指南](NOTIFICATION_GUIDE.md) - HA 发送通知到 MoviePilot
- [更新日志](CHANGELOG.md) - 版本历史

---

**版本**: v1.0.0
**最后更新**: 2025-10-08
**作者**: [@buynow2010](https://github.com/buynow2010)

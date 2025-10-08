# MoviePilot Home Assistant 集成

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/buynow/moviepilot-ha.svg)](https://github.com/buynow/moviepilot-ha/releases)
[![License](https://img.shields.io/github/license/buynow/moviepilot-ha.svg)](LICENSE)

MoviePilot Home Assistant 集成允许您在 Home Assistant 中监控和管理您的 MoviePilot 服务器。

## 📋 功能特性

### 传感器 (10个)

**系统监控 (4个)**:
- **CPU 使用率** - 实时监控 MoviePilot 服务器的 CPU 使用百分比
- **内存使用率** - 监控内存使用情况，包含已用内存 GB 数
- **磁盘使用率** - 监控磁盘使用百分比，包含总容量、已用和剩余空间
- **磁盘可用空间** - 直接显示剩余可用空间（GB）

**下载器 (1个)**:
- **下载速度** - 实时显示下载器的下载速度，包含累计下载量

**任务监控 (1个)**:
- **运行中任务** - 显示当前运行中的任务数量，包含任务名称列表

**媒体统计 (4个)**:
- **电影数量** - 媒体库中的电影总数
- **剧集数量** - 媒体库中的剧集总数
- **剧集集数** - 所有剧集的总集数
- **用户数量** - 系统用户数量

### 二进制传感器 (3个)

- **在线状态** - MoviePilot 服务器连接状态
- **有任务运行** - 是否有任务正在运行，显示运行中和等待中的任务数量
- **下载中** - 下载器是否正在下载，显示下载和上传速度

### 通知服务

- **moviepilot.send_notification** - 发送通知到 MoviePilot 服务器
  - 支持自定义标题和消息
  - 可在自动化和脚本中调用
  - 在开发工具→服务中可见

## 📦 安装

### 方法一：通过 HACS 安装（推荐）

1. 在 HACS 中点击右上角的三个点
2. 选择 "自定义存储库"
3. 添加仓库 URL：`https://github.com/buynow/moviepilot-ha`
4. 类别选择：`Integration`
5. 点击 "添加"
6. 在 HACS 中搜索 "MoviePilot"
7. 点击 "下载"
8. 重启 Home Assistant

### 方法二：手动安装

1. 下载最新版本的 [Releases](https://github.com/buynow/moviepilot-ha/releases)
2. 将 `moviepilot` 文件夹复制到 Home Assistant 配置目录的 `custom_components` 文件夹中
3. 重启 Home Assistant

## ⚙️ 配置

### 前置准备

1. 确保您的 MoviePilot 服务器正在运行
2. 在 MoviePilot 的 **设置 → 安全 → API 令牌** 中获取 API Token

### 添加集成

1. 在 Home Assistant 中，进入 **设置 → 设备与服务**
2. 点击右下角的 **+ 添加集成**
3. 搜索并选择 **MoviePilot**
4. 填写以下信息：
   - **主机地址**：MoviePilot 服务器的 IP 地址或域名（例如：192.168.1.100）
   - **端口**：MoviePilot 服务端口（默认：3000）
   - **API 令牌**：从 MoviePilot 设置中获取的 API Token
   - **集成名称**（可选）：为此集成设置一个友好名称
5. 点击 **提交**

## 📊 实体详细说明

### 传感器

#### sensor.moviepilot_cpu
- **名称**：CPU 使用率
- **单位**：%
- **描述**：MoviePilot 服务器的 CPU 使用率百分比
- **用途**：监控服务器性能，当 CPU 使用率持续过高时可触发告警

#### sensor.moviepilot_memory
- **名称**：内存使用率
- **单位**：%
- **描述**：MoviePilot 服务器的内存使用率百分比
- **额外属性**：
  - `used_gb`：已使用内存（GB）
- **用途**：监控内存占用，防止内存不足导致服务异常

#### sensor.moviepilot_disk
- **名称**：磁盘使用率
- **单位**：%
- **描述**：MoviePilot 监控目录的磁盘使用率百分比
- **额外属性**：
  - `total_storage`：总存储空间（GB）
  - `used_storage`：已用存储空间（GB）
  - `free_storage`：剩余存储空间（GB）
- **用途**：监控磁盘空间，避免磁盘满导致无法下载

#### sensor.moviepilot_disk_free
- **名称**：磁盘可用空间
- **单位**：GB
- **描述**：磁盘剩余可用空间（直接数值）
- **用途**：快速查看剩余空间，可设置阈值告警

#### sensor.moviepilot_downloader_speed
- **名称**：下载速度
- **单位**：B/s（字节/秒）
- **描述**：下载器当前下载速度
- **额外属性**：
  - `total_downloaded`：累计下载量（GB）
- **用途**：实时监控下载速度，统计总下载量

#### sensor.moviepilot_running_tasks
- **名称**：运行中任务
- **单位**：个
- **描述**：当前正在运行的任务数量
- **额外属性**：
  - `task_names`：运行中的任务名称列表
- **用途**：查看当前有哪些任务正在执行

#### sensor.moviepilot_movie_count
- **名称**：电影数量
- **单位**：个
- **描述**：媒体库中的电影总数
- **用途**：监控媒体库增长，统计电影收藏

#### sensor.moviepilot_tv_count
- **名称**：剧集数量
- **单位**：个
- **描述**：媒体库中的剧集总数
- **用途**：监控剧集收藏数量

#### sensor.moviepilot_episode_count
- **名称**：剧集集数
- **单位**：个
- **描述**：所有剧集的总集数
- **用途**：统计实际的剧集集数

#### sensor.moviepilot_user_count
- **名称**：用户数量
- **单位**：个
- **描述**：系统用户数量
- **用途**：监控系统用户变化

### 二进制传感器

#### binary_sensor.moviepilot_online
- **名称**：在线状态
- **设备类型**：connectivity
- **描述**：MoviePilot 服务器是否在线
- **状态**：
  - `on`：在线
  - `off`：离线
- **用途**：监控服务器连接状态，离线时发送通知

#### binary_sensor.moviepilot_tasks_running
- **名称**：有任务运行
- **设备类型**：running
- **描述**：是否有任务正在运行
- **额外属性**：
  - `running_count`：运行中任务数量
  - `pending_count`：等待中任务数量
- **状态**：
  - `on`：有任务运行
  - `off`：空闲
- **用途**：监控任务执行状态

#### binary_sensor.moviepilot_downloading
- **名称**：下载中
- **设备类型**：running
- **描述**：下载器是否正在下载
- **额外属性**：
  - `download_speed`：下载速度（B/s）
  - `upload_speed`：上传速度（B/s）
- **状态**：
  - `on`：下载中
  - `off`：空闲
- **用途**：快速判断是否正在下载

### 通知服务

#### moviepilot.send_notification
- **服务名称**：moviepilot.send_notification
- **描述**：发送通知消息到 MoviePilot 服务器
- **参数**：
  - `title`：通知标题（必需）
  - `message`：通知内容（必需）
- **使用示例**：
  ```yaml
  service: moviepilot.send_notification
  data:
    title: "磁盘空间警告"
    message: "剩余空间仅 50GB，请及时清理！"
  ```
- **用途**：从 Home Assistant 向 MoviePilot 发送通知消息
- **位置**：开发工具 → 服务 → moviepilot.send_notification

## 🎨 Lovelace 卡片示例

### 完整监控卡片

```yaml
type: entities
title: MoviePilot 完整监控
entities:
  - entity: binary_sensor.moviepilot_online
    name: 服务器状态
  - entity: sensor.moviepilot_cpu
    name: CPU 使用率
  - entity: sensor.moviepilot_memory
    name: 内存使用率
  - entity: sensor.moviepilot_disk
    name: 磁盘使用率
  - entity: sensor.moviepilot_disk_free
    name: 剩余空间
  - entity: sensor.moviepilot_movie_count
    name: 电影数量
  - entity: sensor.moviepilot_tv_count
    name: 剧集数量
  - entity: sensor.moviepilot_episode_count
    name: 集数统计
```

### 系统监控卡片

```yaml
type: entities
title: MoviePilot 系统监控
entities:
  - entity: binary_sensor.moviepilot_online
    name: 服务器状态
  - entity: sensor.moviepilot_cpu
    name: CPU 使用率
  - entity: sensor.moviepilot_memory
    name: 内存使用率
  - entity: sensor.moviepilot_disk
    name: 磁盘使用率
  - entity: sensor.moviepilot_disk_free
    name: 剩余空间
```

### 下载监控卡片

```yaml
type: entities
title: MoviePilot 下载状态
entities:
  - entity: binary_sensor.moviepilot_downloading
    name: 下载状态
  - entity: sensor.moviepilot_downloader_speed
    name: 下载速度
  - entity: binary_sensor.moviepilot_tasks_running
    name: 任务状态
  - entity: sensor.moviepilot_running_tasks
    name: 运行中任务
```

### 仪表板卡片

```yaml
type: gauge
entity: sensor.moviepilot_disk
name: 磁盘使用率
min: 0
max: 100
severity:
  green: 0
  yellow: 70
  red: 90
```

### Markdown 卡片（详细信息）

```yaml
type: markdown
content: |
  ## MoviePilot 状态

  **在线状态**: {{ states('binary_sensor.moviepilot_online') }}

  **系统资源**:
  - CPU: {{ states('sensor.moviepilot_cpu') }}%
  - 内存: {{ states('sensor.moviepilot_memory') }}% ({{ state_attr('sensor.moviepilot_memory', 'used_gb') }} GB)
  - 磁盘: {{ states('sensor.moviepilot_disk') }}% (剩余 {{ states('sensor.moviepilot_disk_free') }} GB)

  **下载状态**:
  - 下载速度: {{ (states('sensor.moviepilot_downloader_speed') | float / 1024 / 1024) | round(2) }} MB/s
  - 累计下载: {{ state_attr('sensor.moviepilot_downloader_speed', 'total_downloaded') }} GB

  **任务状态**:
  - 运行中任务: {{ states('sensor.moviepilot_running_tasks') }} 个
```

## 🤖 自动化示例

### 磁盘空间不足告警（使用MoviePilot通知）

```yaml
automation:
  - alias: "MoviePilot 磁盘空间不足"
    trigger:
      - platform: numeric_state
        entity_id: sensor.moviepilot_disk_free
        below: 100  # 剩余空间低于 100GB
    action:
      - service: moviepilot.send_notification
        data:
          title: "⚠️ 磁盘空间不足"
          message: "剩余空间仅 {{ states('sensor.moviepilot_disk_free') }} GB，请及时清理！"
      - service: notify.mobile_app
        data:
          title: "⚠️ MoviePilot 磁盘空间不足"
          message: "剩余空间仅 {{ states('sensor.moviepilot_disk_free') }} GB，请及时清理！"
```

### 新电影入库通知

```yaml
automation:
  - alias: "MoviePilot 电影数量变化"
    trigger:
      - platform: state
        entity_id: sensor.moviepilot_movie_count
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state | int > trigger.from_state.state | int }}"
    action:
      - service: notify.mobile_app
        data:
          title: "🎬 新电影入库"
          message: "媒体库新增 {{ trigger.to_state.state | int - trigger.from_state.state | int }} 部电影！总计 {{ states('sensor.moviepilot_movie_count') }} 部"
```

### 服务器离线通知

```yaml
automation:
  - alias: "MoviePilot 服务器离线"
    trigger:
      - platform: state
        entity_id: binary_sensor.moviepilot_online
        to: "off"
        for:
          minutes: 2
    action:
      - service: notify.mobile_app
        data:
          title: "🔴 MoviePilot 离线"
          message: "MoviePilot 服务器已离线超过 2 分钟！"
```

### 下载完成通知

```yaml
automation:
  - alias: "MoviePilot 下载完成"
    trigger:
      - platform: state
        entity_id: binary_sensor.moviepilot_downloading
        from: "on"
        to: "off"
    condition:
      - condition: state
        entity_id: binary_sensor.moviepilot_online
        state: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "✅ MoviePilot 下载任务完成"
          message: "累计下载: {{ state_attr('sensor.moviepilot_downloader_speed', 'total_downloaded') }} GB"
```

### CPU 使用率过高告警

```yaml
automation:
  - alias: "MoviePilot CPU 使用率过高"
    trigger:
      - platform: numeric_state
        entity_id: sensor.moviepilot_cpu
        above: 90
        for:
          minutes: 5
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ MoviePilot CPU 使用率过高"
          message: "CPU 使用率已超过 90% 并持续 5 分钟"
```

## 🔧 故障排查

### 无法连接到 MoviePilot

1. 确认 MoviePilot 服务器正在运行
2. 检查 IP 地址和端口是否正确
3. 确认 Home Assistant 能够访问 MoviePilot 服务器网络
4. 检查防火墙设置是否阻止了连接

### API 令牌无效

1. 在 MoviePilot 设置中重新生成 API Token
2. 在 Home Assistant 集成中更新 API Token
3. 确保复制 Token 时没有多余的空格

### 实体状态为 unavailable

1. 检查 MoviePilot 服务器是否在线
2. 查看 Home Assistant 日志中的错误信息
3. 尝试重新加载集成
4. 检查 MoviePilot API 版本是否兼容（要求 v2.0+）

### 数据更新缓慢

- 默认更新间隔为 30 秒，这是正常的
- 如果数据长时间不更新，检查网络连接和 MoviePilot 响应速度

## ❓ 常见问题

**Q: 这个集成支持哪些版本的 MoviePilot？**
A: 支持 MoviePilot v2.0 及以上版本。

**Q: 可以同时添加多个 MoviePilot 服务器吗？**
A: 可以，您可以添加多个集成实例，每个实例对应一个 MoviePilot 服务器。

**Q: 为什么没有搜索和下载功能？**
A: v4.0.0 版本专注于监控功能，搜索和下载功能需要更高级别的 API 权限，暂不支持。

**Q: 实体数量是多少？**
A: 总计 13 个实体 + 1个服务：10 个传感器（系统监控 4 个 + 下载器 1 个 + 任务 1 个 + 媒体统计 4 个）+ 3 个二进制传感器 + moviepilot.send_notification 服务。

**Q: 如何使用通知服务？**
A: 在自动化或脚本中使用 `moviepilot.send_notification` 服务，可以向 MoviePilot 发送通知消息。在开发工具→服务中可以找到并测试此服务。

**Q: 如何更改更新频率？**
A: 目前更新频率固定为 30 秒，暂不支持自定义。

**Q: 是否支持 HTTPS？**
A: 支持，但目前默认禁用 SSL 验证。如需启用，请修改代码中的 `verify_ssl` 参数。

## 📝 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解详细的版本更新历史。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

## 🔗 相关链接

- [MoviePilot 官方项目](https://github.com/jxxghp/MoviePilot)
- [问题反馈](https://github.com/buynow/moviepilot-ha/issues)
- [Home Assistant 官网](https://www.home-assistant.io/)

---

**注意**：本集成为非官方第三方集成，与 MoviePilot 官方无关。

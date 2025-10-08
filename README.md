# MoviePilot Home Assistant 集成

将 MoviePilot 完美集成到 Home Assistant，实现双向通知功能和完整的状态监控。

## ✨ 功能特性

### 📊 状态监控（12 个传感器）

#### 系统监控 (4个)
- **CPU 使用率** - 实时 CPU 占用百分比
- **内存使用率** - 内存占用百分比和已用量
- **磁盘使用率** - 磁盘占用百分比
- **磁盘剩余空间** - 可用磁盘空间（GB）

#### 下载器 (1个)
- **下载速度** - 当前下载速度（MB/s）

#### 任务管理 (1个)
- **运行中任务** - 当前正在运行的任务数量

#### 媒体统计 (4个)
- **电影数量** - 媒体库中的电影总数
- **剧集数量** - 媒体库中的剧集总数
- **剧集集数** - 剧集的总集数
- **用户数量** - 媒体服务器用户数

#### 消息通知 (2个) ⭐ 新增
- **下载通知** - 监控下载状态并触发事件
- **整理通知** - 监控整理状态并触发事件

### 🔔 双向通知功能

#### 1. Home Assistant → MoviePilot
从 HA 向 MoviePilot 发送通知：
```yaml
service: notify.moviepilot
data:
  title: "通知标题"
  message: "通知内容"
  data:
    type: "Manual"  # Manual/System/Download/Transfer
```

#### 2. MoviePilot → Home Assistant ⭐ 新增
自动接收 MoviePilot 的状态变化通知：
- 下载开始/完成
- 整理开始/完成
- 触发 `moviepilot_notification` 事件

### 🔌 二进制传感器 (3个)

- **在线状态** - MoviePilot 服务是否在线
- **任务运行状态** - 是否有任务正在运行
- **下载状态** - 是否正在下载

## 📥 安装方法

### 通过 HACS 安装（推荐）

1. 打开 HACS
2. 点击 "集成"
3. 点击右上角的 "⋮" 菜单
4. 选择 "自定义存储库"
5. 输入此仓库地址: `https://github.com/buynow2010/Moviepilot-HA`
6. 类别选择 "Integration"
7. 点击 "添加"
8. 在 HACS 中搜索 "MoviePilot"
9. 点击 "下载"
10. 重启 Home Assistant

### 手动安装

1. 下载最新版本
2. 解压到 `custom_components/moviepilot/` 目录
3. 重启 Home Assistant

## ⚙️ 配置

### 1. 添加集成

1. 进入 `配置` → `设备与服务`
2. 点击 `+ 添加集成`
3. 搜索 "MoviePilot"
4. 输入配置信息：
   - **主机地址**: MoviePilot 服务器地址（如 `ecorehome.cn`）
   - **端口**: 端口号（默认 3000）
   - **API Token**: MoviePilot API 令牌

### 2. 获取 API Token

在 MoviePilot 中获取 API Token：
1. 登录 MoviePilot Web 界面
2. 进入 `设置` → `API`
3. 复制 Token

## 🎯 使用示例

### 接收 MoviePilot 通知到 Home Assistant

创建自动化来接收 MoviePilot 的通知：

```yaml
# configuration.yaml 或 automations.yaml

automation:
  # 接收所有通知
  - alias: "MoviePilot 通知转发"
    trigger:
      - platform: event
        event_type: moviepilot_notification
    action:
      # 显示在 HA 中
      - service: persistent_notification.create
        data:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}"

      # 发送到手机
      - service: notify.mobile_app
        data:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}"

  # 下载完成通知
  - alias: "MoviePilot 下载完成"
    trigger:
      - platform: event
        event_type: moviepilot_notification
        event_data:
          type: "Download"
    condition:
      - condition: template
        value_template: "{{ '完成' in trigger.event.data.title }}"
    action:
      - service: notify.mobile_app
        data:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}"
          data:
            importance: high

  # 整理完成后刷新媒体库
  - alias: "整理完成刷新Plex"
    trigger:
      - platform: event
        event_type: moviepilot_notification
        event_data:
          type: "Transfer"
    condition:
      - condition: template
        value_template: "{{ '完成' in trigger.event.data.title }}"
    action:
      - service: plex.scan_library
        data:
          library_name: "Movies"
```

### 从 Home Assistant 发送通知到 MoviePilot

```yaml
automation:
  # 磁盘空间警告
  - alias: "磁盘空间不足通知"
    trigger:
      - platform: numeric_state
        entity_id: sensor.moviepilot_disk_usage
        above: 90
    action:
      - service: notify.moviepilot
        data:
          title: "⚠️ 磁盘空间告急"
          message: "使用率: {{ states('sensor.moviepilot_disk_usage') }}%"
          data:
            type: "System"

  # 下载完成通知
  - alias: "通知下载完成"
    trigger:
      - platform: state
        entity_id: binary_sensor.moviepilot_downloading
        from: "on"
        to: "off"
    action:
      - service: moviepilot.send_notification
        data:
          title: "✅ 下载完成"
          message: "所有下载任务已完成"
          type: "Download"
```

### Lovelace 仪表板卡片

```yaml
type: entities
title: MoviePilot 状态
entities:
  - entity: sensor.moviepilot_cpu_usage
  - entity: sensor.moviepilot_memory_usage
  - entity: sensor.moviepilot_disk_usage
  - entity: sensor.moviepilot_download_speed
  - entity: sensor.moviepilot_running_tasks
  - entity: sensor.moviepilot_下载通知
  - entity: sensor.moviepilot_整理通知
  - entity: binary_sensor.moviepilot_online
  - entity: binary_sensor.moviepilot_downloading
```

## 📚 详细文档

- **[通知接收指南](RECEIVE_NOTIFICATIONS.md)** - 如何接收 MoviePilot 发送的通知
- **[通知发送指南](NOTIFICATION_GUIDE.md)** - 如何从 HA 发送通知到 MoviePilot

## 🔧 服务

### notify.moviepilot

标准 Home Assistant notify 服务：

```yaml
service: notify.moviepilot
data:
  title: "标题"
  message: "消息内容"
  data:
    type: "Manual"  # Manual, System, Download, Transfer
```

### moviepilot.send_notification

自定义通知服务：

```yaml
service: moviepilot.send_notification
data:
  title: "标题"
  message: "消息内容"
  type: "System"  # Manual, System, Download, Transfer
```

## 🎨 通知类型

| 类型 | 说明 | 使用场景 |
|------|------|----------|
| `Manual` | 手动通知（默认） | 一般性通知、测试 |
| `System` | 系统通知 | 系统状态、警告、错误 |
| `Download` | 下载通知 | 下载任务完成、失败 |
| `Transfer` | 整理通知 | 文件整理、移动完成 |

## 🔍 事件

### moviepilot_notification

当 MoviePilot 状态变化时触发的事件。

**事件数据结构:**
```python
{
    "type": "Download",  # Download 或 Transfer
    "title": "✅ 下载完成",
    "message": "累计下载: 15.2 GB",
    "timestamp": "2025-10-08T21:00:00",
    "source": "moviepilot"
}
```

**使用示例:**
```yaml
automation:
  - alias: "监听 MoviePilot 事件"
    trigger:
      - platform: event
        event_type: moviepilot_notification
    action:
      - service: logbook.log
        data:
          name: "MoviePilot"
          message: "{{ trigger.event.data.title }}: {{ trigger.event.data.message }}"
```

## ⚙️ 配置选项

在集成配置中可以设置：

- **扫描间隔**: 数据更新频率（默认 30 秒，范围 10-300 秒）

## 🐛 故障排查

### 没有收到通知

1. 检查传感器状态:
   - `sensor.moviepilot_下载通知`
   - `sensor.moviepilot_整理通知`

2. 启用调试日志:
   ```yaml
   logger:
     logs:
       custom_components.moviepilot: debug
   ```

3. 在开发者工具查看事件是否触发:
   - 事件类型: `moviepilot_notification`

### 无法连接

- 检查 MoviePilot 服务是否运行
- 验证主机地址和端口
- 确认 API Token 正确
- 检查网络连接

### 数据不更新

- 检查 `binary_sensor.moviepilot_online` 状态
- 查看 Home Assistant 日志
- 尝试重新加载集成

## 📊 系统要求

- Home Assistant 2024.1.0 或更高版本
- MoviePilot V2 或更高版本
- Python 3.11 或更高版本

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [Home Assistant](https://www.home-assistant.io/)
- [MoviePilot](https://github.com/jxxghp/MoviePilot)

## 📞 支持

- [GitHub Issues](https://github.com/buynow2010/Moviepilot-HA/issues)
- [MoviePilot API 文档](https://api.movie-pilot.org)

---

**版本**: v2.0.0
**最后更新**: 2025-10-08
**作者**: [@buynow2010](https://github.com/buynow2010)

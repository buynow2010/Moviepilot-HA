# MoviePilot for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/buynow2010/Moviepilot-HA.svg)](https://github.com/buynow2010/Moviepilot-HA/releases)
[![License](https://img.shields.io/github/license/buynow2010/Moviepilot-HA.svg)](LICENSE)

将 MoviePilot 媒体管理平台无缝集成到 Home Assistant，实现系统监控、状态跟踪和双向通知。

[English](README_EN.md) | 简体中文

---

## 功能特性

### 📊 监控传感器（15个）
- **系统监控**: CPU、内存、磁盘使用率和可用空间
- **下载管理**: 下载速度和任务状态
- **媒体统计**: 电影、剧集数量和用户统计
- **状态监控**: 下载和整理状态通知

### 🔔 双向通知
- **接收通知**: Webhook 实时推送 + 状态变化监控
- **发送通知**: 标准 notify 服务，支持 4 种通知类型

---

## 安装

### 通过 HACS（推荐）

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=buynow2010&repository=Moviepilot-HA&category=integration)

或手动添加：
1. HACS → 集成 → 右上角菜单 → 自定义存储库
2. 输入: `https://github.com/buynow2010/Moviepilot-HA`
3. 类别: Integration → 添加
4. 搜索 "MoviePilot" → 下载
5. 重启 Home Assistant

### 手动安装

1. 下载 [最新版本](https://github.com/buynow2010/Moviepilot-HA/releases)
2. 解压到 `custom_components/moviepilot/`
3. 重启 Home Assistant

---

## 配置

### 1. 添加集成

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=moviepilot)

或手动: **设置** → **设备与服务** → **添加集成** → 搜索 **MoviePilot**

配置信息：
- **主机**: MoviePilot 服务器地址（如 `192.168.1.100`）
- **端口**: 默认 `3000`
- **API Token**: 在 MoviePilot → 设置 → API 中获取

### 2. Webhook 通知（可选）

安装后查看 HA 日志获取 Webhook URL，在 MoviePilot 中配置：

**设置** → **通知** → **添加 Webhook**:
```
URL: http://你的HA地址:8123/api/moviepilot/webhook
方法: POST
请求体: {"title": "{{title}}", "text": "{{message}}", "type": "{{type}}"}
```

---

## 使用示例

### 接收通知

```yaml
automation:
  - alias: "MoviePilot 通知"
    trigger:
      - platform: event
        event_type: moviepilot_notification
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}"
```

### 发送通知

```yaml
automation:
  - alias: "磁盘空间警告"
    trigger:
      - platform: numeric_state
        entity_id: sensor.moviepilot_disk_usage
        above: 90
    action:
      - service: notify.moviepilot
        data:
          title: "磁盘空间不足"
          message: "使用率已达 {{ states('sensor.moviepilot_disk_usage') }}%"
          data:
            type: "System"
```

### Lovelace 卡片

```yaml
type: entities
title: MoviePilot
entities:
  - sensor.moviepilot_cpu_usage
  - sensor.moviepilot_memory_usage
  - sensor.moviepilot_disk_usage
  - sensor.moviepilot_download_speed
  - binary_sensor.moviepilot_online
```

---

## 实体列表

### 传感器（12个）
| 实体 ID | 说明 |
|---------|------|
| `sensor.moviepilot_cpu_usage` | CPU 使用率 (%) |
| `sensor.moviepilot_memory_usage` | 内存使用率 (%) |
| `sensor.moviepilot_disk_usage` | 磁盘使用率 (%) |
| `sensor.moviepilot_disk_free` | 磁盘可用空间 (GB) |
| `sensor.moviepilot_download_speed` | 下载速度 (B/s) |
| `sensor.moviepilot_running_tasks` | 运行中任务数 |
| `sensor.moviepilot_movie_count` | 电影数量 |
| `sensor.moviepilot_tv_count` | 剧集数量 |
| `sensor.moviepilot_episode_count` | 剧集集数 |
| `sensor.moviepilot_user_count` | 用户数量 |
| `sensor.moviepilot_下载通知` | 下载状态监控 |
| `sensor.moviepilot_整理通知` | 整理状态监控 |

### 二进制传感器（3个）
- `binary_sensor.moviepilot_online` - 在线状态
- `binary_sensor.moviepilot_tasks_running` - 任务运行状态
- `binary_sensor.moviepilot_downloading` - 下载状态

---

## 服务

### notify.moviepilot

```yaml
service: notify.moviepilot
data:
  title: "标题"
  message: "内容"
  data:
    type: "Manual"  # Manual/System/Download/Transfer
```

### moviepilot.send_notification

```yaml
service: moviepilot.send_notification
data:
  title: "标题"
  message: "内容"
  type: "System"
```

---

## 事件

### moviepilot_notification

MoviePilot 状态变化或 Webhook 接收通知时触发

事件数据:
```python
{
    "type": "Download",              # 通知类型
    "title": "下载完成",              # 标题
    "message": "累计下载: 15.2 GB",   # 内容
    "timestamp": "2025-10-08T...",   # 时间戳
    "source": "moviepilot_webhook"   # 来源
}
```

---

## 故障排查

### 启用调试日志

```yaml
logger:
  logs:
    custom_components.moviepilot: debug
```

### 常见问题

**无法连接**
- 检查 MoviePilot 是否运行
- 验证主机地址和端口
- 确认 API Token 有效

**无法接收通知**
- 查看 HA 日志中的 Webhook URL
- 确认 MoviePilot 中 Webhook 配置正确
- 检查 `sensor.moviepilot_下载通知` 状态

---

## 系统要求

- Home Assistant 2024.1.0+
- MoviePilot V2+
- Python 3.11+

---

## 更新日志

查看 [CHANGELOG.md](CHANGELOG.md)

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 链接

- [问题反馈](https://github.com/buynow2010/Moviepilot-HA/issues)
- [讨论区](https://github.com/buynow2010/Moviepilot-HA/discussions)
- [MoviePilot](https://github.com/jxxghp/MoviePilot)

---

**Made with ❤️ for Home Assistant Community**

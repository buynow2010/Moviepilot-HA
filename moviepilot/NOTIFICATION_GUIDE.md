# MoviePilot 通知服务使用指南

MoviePilot Home Assistant 集成现在提供了三种方式来发送通知到 MoviePilot 服务器。

## 🔔 通知方式对比

| 方式 | 服务名称 | 推荐度 | 适用场景 |
|------|---------|--------|---------|
| **标准 Notify** | `notify.moviepilot` | ⭐⭐⭐⭐⭐ | 所有场景（推荐） |
| **自定义服务** | `moviepilot.send_notification` | ⭐⭐⭐⭐ | 需要指定类型的场景 |

---

## 方式 1: 标准 Notify 服务（推荐）

这是最标准的 Home Assistant 通知方式，符合所有 HA 规范。

### 基础用法

```yaml
# 在自动化或脚本中
action:
  - service: notify.moviepilot
    data:
      title: "下载完成"
      message: "电影《流浪地球2》已下载完成"
```

### 高级用法（带类型）

```yaml
action:
  - service: notify.moviepilot
    data:
      title: "磁盘空间警告"
      message: "剩余空间不足 100GB，请及时清理"
      data:
        type: "System"  # 可选: Manual, System, Download, Transfer
```

### 自动化示例 1：下载完成通知

```yaml
automation:
  - alias: "MoviePilot 下载完成通知"
    trigger:
      - platform: state
        entity_id: binary_sensor.moviepilot_downloading
        from: "on"
        to: "off"
    action:
      - service: notify.moviepilot
        data:
          title: "下载完成"
          message: "所有下载任务已完成"
          data:
            type: "Download"
```

### 自动化示例 2：磁盘空间监控

```yaml
automation:
  - alias: "MoviePilot 磁盘空间警告"
    trigger:
      - platform: numeric_state
        entity_id: sensor.moviepilot_disk
        above: 90
    action:
      - service: notify.moviepilot
        data:
          title: "磁盘空间警告"
          message: >
            磁盘使用率已达 {{ states('sensor.moviepilot_disk') }}%
            可用空间: {{ states('sensor.moviepilot_disk_free') }}GB
          data:
            type: "System"
```

---

## 方式 2: 自定义服务

直接调用 MoviePilot 专用服务，支持所有参数。

### 基础用法

```yaml
action:
  - service: moviepilot.send_notification
    data:
      title: "新电影添加"
      message: "已添加《三体》到下载队列"
      type: "Download"
```

### 自动化示例：任务状态监控

```yaml
automation:
  - alias: "MoviePilot 任务开始通知"
    trigger:
      - platform: state
        entity_id: binary_sensor.moviepilot_tasks_running
        to: "on"
    action:
      - service: moviepilot.send_notification
        data:
          title: "任务开始"
          message: >
            当前运行任务数: {{ states('sensor.moviepilot_running_tasks') }}
            等待任务数: {{ state_attr('binary_sensor.moviepilot_tasks_running', 'pending_count') }}
          type: "System"
```

---

## 📊 通知类型说明

| 类型 | 值 | 用途 |
|------|-----|------|
| 手动 | `Manual` | 手动触发的通知（默认） |
| 系统 | `System` | 系统状态、警告等 |
| 下载 | `Download` | 下载相关通知 |
| 整理 | `Transfer` | 文件整理、转移相关 |

---

## 🎯 实用自动化场景

### 场景 1: 每日媒体库统计

```yaml
automation:
  - alias: "MoviePilot 每日统计报告"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: notify.moviepilot
        data:
          title: "📊 每日媒体库统计"
          message: |
            🎬 电影: {{ states('sensor.moviepilot_movie_count') }} 部
            📺 剧集: {{ states('sensor.moviepilot_tv_count') }} 部
            📼 总集数: {{ states('sensor.moviepilot_episode_count') }} 集
            💾 磁盘使用: {{ states('sensor.moviepilot_disk') }}%
            📥 今日下载: {{ (states('sensor.moviepilot_downloader_speed')|float / 1048576) | round(2) }} MB/s
          data:
            type: "System"
```

### 场景 2: 下载速度异常警告

```yaml
automation:
  - alias: "MoviePilot 下载速度过低警告"
    trigger:
      - platform: numeric_state
        entity_id: sensor.moviepilot_downloader_speed
        below: 1048576  # 1 MB/s
        for:
          minutes: 5
    condition:
      - condition: state
        entity_id: binary_sensor.moviepilot_downloading
        state: "on"
    action:
      - service: notify.moviepilot
        data:
          title: "⚠️ 下载速度异常"
          message: >
            当前下载速度过低: {{ (states('sensor.moviepilot_downloader_speed')|float / 1048576) | round(2) }} MB/s
            请检查网络连接和下载器状态
          data:
            type: "Download"
```

### 场景 3: 离线状态通知

```yaml
automation:
  - alias: "MoviePilot 离线警告"
    trigger:
      - platform: state
        entity_id: binary_sensor.moviepilot_online
        to: "off"
        for:
          minutes: 5
    action:
      - service: notify.mobile_app  # 发送到手机
        data:
          title: "MoviePilot 离线"
          message: "MoviePilot 服务器已离线超过 5 分钟，请检查！"
```

---

## 🛠️ 开发者指南

### Python 脚本调用

```python
# 在 Home Assistant Python 脚本中
hass.services.call(
    'notify',
    'moviepilot',
    {
        'title': '脚本测试',
        'message': '这是来自 Python 脚本的通知',
        'data': {'type': 'Manual'}
    }
)
```

### Node-RED 调用

```json
{
    "domain": "notify",
    "service": "moviepilot",
    "data": {
        "title": "Node-RED 通知",
        "message": "来自 Node-RED 的消息",
        "data": {
            "type": "System"
        }
    }
}
```

---

## ❓ 常见问题

### Q: notify.moviepilot 服务找不到？

A: 请确保：
1. MoviePilot 集成已正确安装
2. Home Assistant 已重启
3. 在开发者工具 > 服务 中搜索 "moviepilot"

### Q: 通知发送失败？

A: 检查以下项：
1. MoviePilot API Token 是否正确
2. MoviePilot 服务是否在线（检查 `binary_sensor.moviepilot_online`）
3. 查看 Home Assistant 日志：设置 > 系统 > 日志

### Q: 如何查看通知是否成功发送？

A: 查看日志：
```yaml
logger:
  logs:
    custom_components.moviepilot: debug
```

---

## 📚 更多资源

- [MoviePilot 官方文档](https://github.com/jxxghp/MoviePilot)
- [Home Assistant 自动化指南](https://www.home-assistant.io/docs/automation/)
- [集成 GitHub 仓库](https://github.com/buynow2010/Moviepilot-HA)

---

**享受您的 MoviePilot + Home Assistant 通知集成！** 🎬🔔

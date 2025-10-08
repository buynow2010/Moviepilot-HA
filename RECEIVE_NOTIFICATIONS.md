# MoviePilot 通知接收配置指南

## 概述

MoviePilot Home Assistant 集成通过监控状态变化，自动将 MoviePilot 的通知转发到 Home Assistant。

## 工作原理

集成创建了两个特殊的传感器来监控 MoviePilot 状态：

1. **`sensor.moviepilot_下载通知`** - 监控下载状态
2. **`sensor.moviepilot_整理通知`** - 监控整理状态

当状态变化时（如下载开始/完成、整理开始/完成），会触发 `moviepilot_notification` 事件，你可以通过自动化来接收这些通知。

## 📥 接收 MoviePilot 通知

### 方式 1: 使用事件触发自动化（推荐）

```yaml
# configuration.yaml 或 automations.yaml

automation:
  # 接收所有 MoviePilot 通知
  - alias: "MoviePilot 通知转发"
    description: "将 MoviePilot 的通知显示在 Home Assistant 中"
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

      # 同时发送到手机（如果配置了 notify 服务）
      - service: notify.mobile_app_your_phone
        data:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}"
```

### 方式 2: 根据通知类型分别处理

```yaml
automation:
  # 下载完成通知
  - alias: "MoviePilot 下载完成"
    trigger:
      - platform: event
        event_type: moviepilot_notification
        event_data:
          type: "Download"
    action:
      - service: notify.mobile_app
        data:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}"
          data:
            tag: "moviepilot_download"
            group: "moviepilot"
            importance: high

  # 整理完成通知
  - alias: "MoviePilot 整理完成"
    trigger:
      - platform: event
        event_type: moviepilot_notification
        event_data:
          type: "Transfer"
    action:
      - service: notify.mobile_app
        data:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}"
          data:
            tag: "moviepilot_transfer"
            group: "moviepilot"
```

### 方式 3: 监控传感器状态变化

```yaml
automation:
  # 监控下载状态变化
  - alias: "MoviePilot 下载状态监控"
    trigger:
      - platform: state
        entity_id: sensor.moviepilot_下载通知
        to: "下载完成"
    action:
      - service: persistent_notification.create
        data:
          title: "✅ 下载完成"
          message: "MoviePilot 已完成所有下载任务"

  # 监控整理状态变化
  - alias: "MoviePilot 整理状态监控"
    trigger:
      - platform: state
        entity_id: sensor.moviepilot_整理通知
        to: "整理完成"
    action:
      - service: persistent_notification.create
        data:
          title: "✅ 整理完成"
          message: "文件已整理到媒体库"
```

## 🔔 高级通知配置

### 智能通知 - 只在特定时间通知

```yaml
automation:
  - alias: "MoviePilot 智能通知"
    trigger:
      - platform: event
        event_type: moviepilot_notification
    condition:
      # 只在晚上 6 点到 11 点之间通知
      - condition: time
        after: "18:00:00"
        before: "23:00:00"
    action:
      - service: notify.mobile_app
        data:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}"
```

### 语音播报通知

```yaml
automation:
  - alias: "MoviePilot 语音播报"
    trigger:
      - platform: event
        event_type: moviepilot_notification
        event_data:
          type: "Download"
    action:
      - service: tts.google_translate_say
        data:
          entity_id: media_player.living_room
          message: "{{ trigger.event.data.title }}，{{ trigger.event.data.message }}"
```

### 发送到多个通知渠道

```yaml
automation:
  - alias: "MoviePilot 多渠道通知"
    trigger:
      - platform: event
        event_type: moviepilot_notification
    action:
      # 1. Home Assistant 持久通知
      - service: persistent_notification.create
        data:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}"

      # 2. 手机通知
      - service: notify.mobile_app
        data:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}"

      # 3. Telegram 通知
      - service: notify.telegram
        data:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}"

      # 4. 微信通知（如果配置了）
      - service: notify.wechat
        data:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}"
```

## 📊 创建通知历史记录

### 记录所有通知到传感器

```yaml
# configuration.yaml
template:
  - trigger:
      - platform: event
        event_type: moviepilot_notification
    sensor:
      - name: "MoviePilot 最新通知"
        state: "{{ trigger.event.data.title }}"
        attributes:
          message: "{{ trigger.event.data.message }}"
          type: "{{ trigger.event.data.type }}"
          timestamp: "{{ trigger.event.data.timestamp }}"
```

### 记录通知到日志

```yaml
automation:
  - alias: "MoviePilot 通知日志"
    trigger:
      - platform: event
        event_type: moviepilot_notification
    action:
      - service: logbook.log
        data:
          name: "MoviePilot"
          message: "{{ trigger.event.data.title }}: {{ trigger.event.data.message }}"
          entity_id: sensor.moviepilot_cpu_usage
```

## 🎯 实用场景

### 场景 1: 下载完成后自动刷新媒体库

```yaml
automation:
  - alias: "下载完成刷新媒体库"
    trigger:
      - platform: event
        event_type: moviepilot_notification
        event_data:
          type: "Download"
    condition:
      - condition: template
        value_template: "{{ '完成' in trigger.event.data.title }}"
    action:
      # 通知
      - service: notify.mobile_app
        data:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}"

      # 刷新 Plex/Emby/Jellyfin 媒体库
      - service: media_player.scan_media_library
        target:
          entity_id: media_player.plex
```

### 场景 2: 整理完成后通知家人

```yaml
automation:
  - alias: "新片入库通知家人"
    trigger:
      - platform: event
        event_type: moviepilot_notification
        event_data:
          type: "Transfer"
    condition:
      - condition: template
        value_template: "{{ '完成' in trigger.event.data.title }}"
    action:
      # 发送到家庭群组
      - service: notify.family_group
        data:
          title: "🎬 新片入库"
          message: "MoviePilot 已完成整理，可以观影啦！"
```

### 场景 3: 下载中显示进度

```yaml
automation:
  - alias: "显示下载进度"
    trigger:
      - platform: state
        entity_id: sensor.moviepilot_下载通知
        to: "下载中"
    action:
      - service: persistent_notification.create
        data:
          title: "📥 正在下载"
          message: >
            当前下载速度: {{ states('sensor.moviepilot_download_speed') }}
            已下载: {{ state_attr('sensor.moviepilot_download_speed', 'total_downloaded') }}
          notification_id: "moviepilot_downloading"

  # 下载完成时移除进度通知
  - alias: "清除下载进度"
    trigger:
      - platform: state
        entity_id: sensor.moviepilot_下载通知
        from: "下载中"
    action:
      - service: persistent_notification.dismiss
        data:
          notification_id: "moviepilot_downloading"
```

## 🎨 通知样式定制

### 为不同类型通知设置不同图标和颜色

```yaml
automation:
  - alias: "MoviePilot 样式化通知"
    trigger:
      - platform: event
        event_type: moviepilot_notification
    action:
      - service: notify.mobile_app
        data:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}"
          data:
            # 根据类型设置不同图标
            notification_icon: >
              {% if trigger.event.data.type == 'Download' %}
                mdi:download
              {% elif trigger.event.data.type == 'Transfer' %}
                mdi:folder-move
              {% else %}
                mdi:information
              {% endif %}
            # 根据类型设置不同颜色
            color: >
              {% if trigger.event.data.type == 'Download' %}
                blue
              {% elif trigger.event.data.type == 'Transfer' %}
                green
              {% else %}
                orange
              {% endif %}
            # 分组
            group: "moviepilot"
            tag: "moviepilot_{{ trigger.event.data.type }}"
```

## 📱 配置示例完整版

这是一个完整的配置示例，包含所有功能：

```yaml
# configuration.yaml
automation moviepilot_notifications:
  # ========== 基础通知 ==========

  - alias: "MoviePilot 通知中心"
    description: "接收并处理所有 MoviePilot 通知"
    id: moviepilot_notification_center
    mode: queued  # 队列模式，确保不丢失通知
    trigger:
      - platform: event
        event_type: moviepilot_notification
    action:
      # 1. 记录到日志
      - service: logbook.log
        data:
          name: "MoviePilot"
          message: "[{{ trigger.event.data.type }}] {{ trigger.event.data.title }}"

      # 2. 显示持久通知（5分钟后自动消失）
      - service: persistent_notification.create
        data:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}\n\n时间: {{ trigger.event.data.timestamp }}"
          notification_id: "moviepilot_{{ as_timestamp(now()) | int }}"

      # 3. 发送到手机（可选）
      - service: notify.mobile_app
        data:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}"
          data:
            group: "moviepilot"
            tag: "moviepilot_{{ trigger.event.data.type }}"

  # ========== 下载通知 ==========

  - alias: "MoviePilot 下载开始"
    trigger:
      - platform: state
        entity_id: sensor.moviepilot_下载通知
        to: "下载中"
    action:
      - service: notify.mobile_app
        data:
          title: "📥 开始下载"
          message: "MoviePilot 开始下载新内容"

  - alias: "MoviePilot 下载完成"
    trigger:
      - platform: state
        entity_id: sensor.moviepilot_下载通知
        to: "下载完成"
    action:
      - service: notify.mobile_app
        data:
          title: "✅ 下载完成"
          message: "所有下载任务已完成"
          data:
            importance: high

  # ========== 整理通知 ==========

  - alias: "MoviePilot 整理完成"
    trigger:
      - platform: state
        entity_id: sensor.moviepilot_整理通知
        to: "整理完成"
    action:
      - service: notify.mobile_app
        data:
          title: "✅ 整理完成"
          message: "文件已整理到媒体库"

      # 可选: 刷新媒体服务器
      - service: plex.scan_library
        data:
          library_name: "Movies"

# 创建历史记录传感器
template:
  - trigger:
      - platform: event
        event_type: moviepilot_notification
    sensor:
      - name: "MoviePilot 最新通知"
        state: "{{ trigger.event.data.type }}"
        attributes:
          title: "{{ trigger.event.data.title }}"
          message: "{{ trigger.event.data.message }}"
          timestamp: "{{ trigger.event.data.timestamp }}"
```

## 🔍 调试

### 查看事件触发

在 Home Assistant 开发者工具 → 事件 中监听 `moviepilot_notification` 事件：

```yaml
事件类型: moviepilot_notification
```

### 查看传感器状态

在 Home Assistant 开发者工具 → 状态 中查看：
- `sensor.moviepilot_下载通知`
- `sensor.moviepilot_整理通知`

### 启用调试日志

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.moviepilot.message_sensor: debug
```

## ❓ 常见问题

**Q: 没有收到通知？**
- 检查传感器是否正常更新
- 查看 Home Assistant 日志
- 确认自动化已启用

**Q: 通知重复？**
- 检查是否有多个相同的自动化
- 使用 `mode: single` 或 `mode: queued`

**Q: 如何只接收特定类型的通知？**
- 使用事件数据过滤: `event_data: type: "Download"`

---

**版本**: v2.0.0
**最后更新**: 2025-10-08
**作者**: [@buynow2010](https://github.com/buynow2010)

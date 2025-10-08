# MoviePilot Home Assistant 通知服务使用指南

## 📖 概述

MoviePilot Home Assistant 集成提供了完整的通知服务，让你可以从 Home Assistant 向 MoviePilot 发送各种类型的通知消息。

## ✨ 功能特性

- ✅ 标准 Home Assistant `notify` 服务支持
- ✅ 自定义 `moviepilot.send_notification` 服务
- ✅ 支持 4 种通知类型（Manual、System、Download、Transfer）
- ✅ 完善的错误处理和日志记录
- ✅ 参数验证和自动降级
- ✅ 支持自动化和脚本调用

## 🎯 通知类型

| 类型 | 说明 | 使用场景 |
|------|------|----------|
| `Manual` | 手动通知（默认） | 一般性通知、测试 |
| `System` | 系统通知 | 系统状态、警告、错误 |
| `Download` | 下载通知 | 下载任务完成、失败 |
| `Transfer` | 整理通知 | 文件整理、移动完成 |

## 📝 使用方法

### 方法 1: 标准 notify 服务（推荐）

这是 Home Assistant 标准的通知服务调用方式，与其他通知平台保持一致。

```yaml
service: notify.moviepilot
data:
  title: "通知标题"
  message: "通知内容"
  data:
    type: "Manual"  # 可选，默认为 Manual
```

#### 示例

```yaml
# 简单通知（使用默认类型）
service: notify.moviepilot
data:
  title: "Hello MoviePilot"
  message: "这是一条测试通知"

# 系统通知
service: notify.moviepilot
data:
  title: "⚠️ 系统警告"
  message: "磁盘空间不足"
  data:
    type: "System"

# 下载通知
service: notify.moviepilot
data:
  title: "📥 下载完成"
  message: "电影《阿凡达》已下载完成"
  data:
    type: "Download"
```

### 方法 2: 自定义服务

使用 MoviePilot 特有的服务，参数更简洁。

```yaml
service: moviepilot.send_notification
data:
  title: "通知标题"
  message: "通知内容"
  type: "System"  # 可选，默认为 Manual
```

#### 示例

```yaml
# 整理完成通知
service: moviepilot.send_notification
data:
  title: "📁 整理完成"
  message: "已将 5 个文件整理到媒体库"
  type: "Transfer"

# 系统通知
service: moviepilot.send_notification
data:
  title: "🖥️ MoviePilot 已重启"
  message: "服务已成功重新启动"
  type: "System"
```

## 🤖 自动化示例

### 示例 1: 磁盘空间监控

当磁盘使用率超过 90% 时发送警告通知。

```yaml
automation:
  - alias: "MoviePilot 磁盘空间警告"
    description: "磁盘使用率超过90%时通知"
    trigger:
      - platform: numeric_state
        entity_id: sensor.moviepilot_disk_usage
        above: 90
    action:
      - service: notify.moviepilot
        data:
          title: "⚠️ 磁盘空间告急"
          message: >
            当前磁盘使用率: {{ states('sensor.moviepilot_disk_usage') }}%
            剩余空间: {{ state_attr('sensor.moviepilot_disk_free', 'free_space') }} GB
            请及时清理！
          data:
            type: "System"
```

### 示例 2: 下载任务监控

当下载任务完成时发送通知。

```yaml
automation:
  - alias: "MoviePilot 下载完成通知"
    description: "下载任务完成时通知"
    trigger:
      - platform: state
        entity_id: binary_sensor.moviepilot_downloading
        from: "on"
        to: "off"
    action:
      - service: notify.moviepilot
        data:
          title: "✅ 下载任务完成"
          message: "所有下载任务已完成处理"
          data:
            type: "Download"
```

### 示例 3: 每日统计报告

每天晚上发送媒体库统计报告。

```yaml
automation:
  - alias: "MoviePilot 每日统计"
    description: "每天晚上发送媒体库统计"
    trigger:
      - platform: time
        at: "23:00:00"
    action:
      - service: notify.moviepilot
        data:
          title: "📊 今日统计"
          message: >
            媒体库统计:
            - 电影: {{ state_attr('sensor.moviepilot_cpu_usage', 'movie_count') }} 部
            - 剧集: {{ state_attr('sensor.moviepilot_cpu_usage', 'tv_count') }} 部
            - 运行任务: {{ states('sensor.moviepilot_running_tasks') }} 个

            系统状态:
            - CPU: {{ states('sensor.moviepilot_cpu_usage') }}%
            - 内存: {{ states('sensor.moviepilot_memory_usage') }}%
            - 磁盘: {{ states('sensor.moviepilot_disk_usage') }}%
          data:
            type: "System"
```

### 示例 4: 任务异常监控

当有任务运行超过 2 小时时发送警告。

```yaml
automation:
  - alias: "MoviePilot 任务超时警告"
    description: "任务运行超过2小时时警告"
    trigger:
      - platform: state
        entity_id: binary_sensor.moviepilot_tasks_running
        to: "on"
        for:
          hours: 2
    action:
      - service: notify.moviepilot
        data:
          title: "⚠️ 任务运行时间过长"
          message: >
            有任务已运行超过 2 小时，可能存在异常。
            当前运行任务数: {{ states('sensor.moviepilot_running_tasks') }}
          data:
            type: "System"
```

### 示例 5: 服务上线/下线通知

当 MoviePilot 服务状态变化时通知。

```yaml
automation:
  - alias: "MoviePilot 服务状态监控"
    description: "MoviePilot上线或下线时通知"
    trigger:
      - platform: state
        entity_id: binary_sensor.moviepilot_online
    action:
      - service: notify.moviepilot
        data:
          title: >
            {% if trigger.to_state.state == 'on' %}
            ✅ MoviePilot 已上线
            {% else %}
            ❌ MoviePilot 已下线
            {% endif %}
          message: >
            服务状态已变更为: {{ trigger.to_state.state }}
            时间: {{ now().strftime('%Y-%m-%d %H:%M:%S') }}
          data:
            type: "System"
```

## 🎨 高级用法

### 在脚本中使用

```yaml
script:
  notify_download_complete:
    alias: "通知下载完成"
    sequence:
      - service: notify.moviepilot
        data:
          title: "{{ title }}"
          message: "{{ message }}"
          data:
            type: "Download"

# 调用脚本
service: script.notify_download_complete
data:
  title: "📥 新电影下载完成"
  message: "{{ movie_name }} 已下载完成"
```

### 条件通知

根据不同条件发送不同类型的通知。

```yaml
automation:
  - alias: "智能通知"
    trigger:
      - platform: state
        entity_id: sensor.moviepilot_disk_usage
    action:
      - choose:
          # 磁盘使用率 > 95% - 紧急警告
          - conditions:
              - condition: numeric_state
                entity_id: sensor.moviepilot_disk_usage
                above: 95
            sequence:
              - service: notify.moviepilot
                data:
                  title: "🚨 磁盘空间严重不足"
                  message: "使用率已达 {{ states('sensor.moviepilot_disk_usage') }}%"
                  data:
                    type: "System"

          # 磁盘使用率 > 90% - 一般警告
          - conditions:
              - condition: numeric_state
                entity_id: sensor.moviepilot_disk_usage
                above: 90
            sequence:
              - service: notify.moviepilot
                data:
                  title: "⚠️ 磁盘空间偏低"
                  message: "使用率: {{ states('sensor.moviepilot_disk_usage') }}%"
                  data:
                    type: "System"
```

### 批量通知

在一个自动化中发送多条通知。

```yaml
automation:
  - alias: "每周总结"
    trigger:
      - platform: time
        at: "20:00:00"
    condition:
      - condition: time
        weekday:
          - sun
    action:
      # 发送统计报告
      - service: notify.moviepilot
        data:
          title: "📊 本周统计"
          message: "本周新增电影: XX 部，剧集: XX 部"
          data:
            type: "System"

      # 延迟1秒
      - delay: "00:00:01"

      # 发送下载报告
      - service: notify.moviepilot
        data:
          title: "📥 本周下载"
          message: "本周下载流量: XX GB"
          data:
            type: "Download"
```

## 🔧 故障排查

### 1. 通知发送失败

**检查项目:**
- 确认 MoviePilot 服务正常运行
- 检查 Home Assistant 日志: `配置` → `日志`
- 验证 API Token 是否正确
- 确认网络连接正常

**日志位置:**
```
Home Assistant 日志中搜索: moviepilot
```

### 2. 看不到 notify.moviepilot 服务

**解决方法:**
- 重启 Home Assistant
- 检查集成是否正确加载: `配置` → `集成` → `MoviePilot`
- 查看日志中是否有错误信息

### 3. 通知类型无效

通知类型必须是以下之一（区分大小写）：
- `Manual`
- `System`
- `Download`
- `Transfer`

如果使用了无效的类型，系统会自动降级为 `Manual` 类型并在日志中记录警告。

### 4. 查看详细日志

在 `configuration.yaml` 中启用调试日志：

```yaml
logger:
  default: info
  logs:
    custom_components.moviepilot: debug
    custom_components.moviepilot.notify: debug
    custom_components.moviepilot.api: debug
```

## 📱 实际应用场景

### 场景 1: 家庭影院自动化

当有新电影整理完成时，通知家人可以观看。

```yaml
automation:
  - alias: "新电影入库通知"
    trigger:
      - platform: state
        entity_id: binary_sensor.moviepilot_tasks_running
        from: "on"
        to: "off"
    condition:
      - condition: state
        entity_id: sensor.moviepilot_movie_count
        state: "not_unavailable"
    action:
      - service: notify.moviepilot
        data:
          title: "🎬 新电影入库"
          message: "新电影已整理完成，可以观看啦！"
          data:
            type: "Transfer"
```

### 场景 2: 资源管理

自动清理磁盘空间的工作流。

```yaml
automation:
  - alias: "自动清理磁盘"
    trigger:
      - platform: numeric_state
        entity_id: sensor.moviepilot_disk_usage
        above: 95
    action:
      # 发送警告
      - service: notify.moviepilot
        data:
          title: "🚨 开始自动清理"
          message: "磁盘空间不足，开始自动清理..."
          data:
            type: "System"

      # 执行清理操作（这里需要自定义脚本）
      - service: shell_command.cleanup_disk

      # 延迟等待清理完成
      - delay: "00:05:00"

      # 发送完成通知
      - service: notify.moviepilot
        data:
          title: "✅ 清理完成"
          message: "当前使用率: {{ states('sensor.moviepilot_disk_usage') }}%"
          data:
            type: "System"
```

### 场景 3: 健康监控面板

创建一个完整的监控自动化。

```yaml
automation:
  - alias: "MoviePilot 健康检查"
    trigger:
      - platform: time_pattern
        hours: "/2"  # 每2小时检查一次
    action:
      - choose:
          # 一切正常
          - conditions:
              - condition: numeric_state
                entity_id: sensor.moviepilot_disk_usage
                below: 80
              - condition: state
                entity_id: binary_sensor.moviepilot_online
                state: "on"
            sequence:
              - service: notify.moviepilot
                data:
                  title: "✅ 系统状态良好"
                  message: "所有指标正常"
                  data:
                    type: "System"

          # 有问题
          - conditions: []
            sequence:
              - service: notify.moviepilot
                data:
                  title: "⚠️ 系统异常"
                  message: "请检查系统状态"
                  data:
                    type: "System"
```

## 🎯 最佳实践

1. **使用有意义的标题**: 标题应该清晰表达通知内容
2. **选择正确的通知类型**: 根据通知性质选择合适的类型
3. **避免频繁通知**: 使用条件和延迟避免通知轰炸
4. **使用模板**: 利用 Home Assistant 模板让通知更动态
5. **监控日志**: 定期检查日志确保通知正常工作

## 📚 相关文档

- [Home Assistant Notify 服务](https://www.home-assistant.io/integrations/notify/)
- [Home Assistant 自动化](https://www.home-assistant.io/docs/automation/)
- [MoviePilot API 文档](https://api.movie-pilot.org)
- [集成主页](https://github.com/buynow2010/Moviepilot-HA)

## 💬 技术支持

如遇问题，请：
1. 查看本文档的故障排查部分
2. 检查 Home Assistant 日志
3. 在 [GitHub Issues](https://github.com/buynow2010/Moviepilot-HA/issues) 提交问题

---

**版本**: v1.0.0
**最后更新**: 2025-10-08
**作者**: [@buynow2010](https://github.com/buynow2010)

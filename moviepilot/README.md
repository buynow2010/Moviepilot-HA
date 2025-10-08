# MoviePilot Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/buynow2010/Moviepilot-HA.svg)](https://github.com/buynow2010/Moviepilot-HA/releases)
[![License](https://img.shields.io/github/license/buynow2010/Moviepilot-HA.svg)](LICENSE)

将 MoviePilot 完美集成到 Home Assistant 中，实时监控媒体服务器状态、下载进度和系统资源。

**版本**: v1.0.0
**更新日期**: 2025-10-08

---

## ✨ 特性

### 📊 系统监控 (8个传感器)
- **CPU使用率** - 实时CPU占用百分比
- **内存使用率** - 内存占用百分比
- **内存使用量** - 实际内存使用量 (GB)
- **磁盘使用率** - 磁盘空间占用百分比
- **磁盘可用空间** - 剩余磁盘空间 (GB)
- **磁盘总空间** - 总磁盘容量 (GB)
- **网络上传速度** - 实时上传速率
- **网络下载速度** - 实时下载速率

### 🎬 媒体库统计 (4个传感器)
- **电影数量** - 媒体库中的电影总数
- **剧集数量** - TV剧集总数
- **集数** - 总集数统计
- **用户数** - MoviePilot用户数

### ⬇️ 下载监控 (4个传感器)
- **下载速度** - 当前下载速率
- **上传速度** - 当前上传速率 (做种)
- **累计下载量** - 总下载数据量 (GB)
- **累计上传量** - 总上传数据量 (GB)

### 📅 任务监控 (2个传感器)
- **运行中任务** - 当前正在执行的任务数
- **等待中任务** - 队列中等待的任务数

### 🔔 通知服务 (NEW!)
- **notify.moviepilot** - 标准 Home Assistant 通知服务
- **moviepilot.send_notification** - 自定义通知服务
- **多种通知类型** - Manual, System, Download, Transfer
- **完整的自动化支持** - 可在所有自动化和脚本中使用

### 🔘 二进制传感器 (4个)
- **在线状态** - MoviePilot服务是否在线
- **有任务运行** - 是否有任务正在运行
- **文件传输中** - 是否在传输/整理文件
- **下载中** - 是否正在下载

### 🎛️ 按钮实体 (2个)
- **刷新数据** - 手动触发数据刷新
- **测试连接** - 测试与MoviePilot的连接

---

## 📦 安装

### 方法1: 通过HACS安装 (推荐)

1. 打开HACS，进入"集成"页面
2. 点击右上角菜单，选择"自定义存储库"
3. 添加此仓库URL
4. 搜索"MoviePilot"并安装
5. 重启Home Assistant

### 方法2: 手动安装

1. 下载此仓库
2. 将 `moviepilot` 文件夹复制到 `config/custom_components/` 目录
3. 重启Home Assistant

---

## ⚙️ 配置

### 获取API Token

1. 登录MoviePilot Web界面
2. 进入 设置 -> API设置
3. 生成或复制API Token

### 添加集成

1. 进入 Home Assistant 设置 -> 设备与服务
2. 点击"添加集成"
3. 搜索"MoviePilot"
4. 输入以下信息：
   - **主机地址**: MoviePilot服务器地址 (如 `192.168.1.100` 或 `moviepilot.example.com`)
   - **端口**: 默认 `3000`
   - **API Token**: 从MoviePilot获取的token
   - **名称**: 自定义名称 (可选)

### 配置选项

安装后可以在集成页面点击"配置"调整：
- **更新间隔**: 数据刷新频率 (10-300秒，默认30秒)

---

## 📱 使用示例

### 通知服务示例

#### 方式 1: 标准 notify 服务（推荐）
```yaml
# 在自动化或脚本中
action:
  - service: notify.moviepilot
    data:
      title: "下载完成"
      message: "电影《流浪地球2》已下载完成"
      data:
        type: "Download"  # 可选: Manual, System, Download, Transfer
```

#### 方式 2: 自定义服务
```yaml
action:
  - service: moviepilot.send_notification
    data:
      title: "磁盘空间警告"
      message: "剩余空间不足 100GB"
      type: "System"
```

📖 **完整通知指南**: 查看 [NOTIFICATION_GUIDE.md](NOTIFICATION_GUIDE.md) 了解更多用法和示例

### Lovelace卡片示例

#### 系统监控卡片
```yaml
type: entities
title: MoviePilot 系统状态
entities:
  - entity: binary_sensor.moviepilot_online
    name: 在线状态
  - entity: sensor.moviepilot_cpu
    name: CPU使用率
  - entity: sensor.moviepilot_memory
    name: 内存使用率
  - entity: sensor.moviepilot_disk
    name: 磁盘使用率
  - entity: sensor.moviepilot_disk_free
    name: 可用空间
```

#### 媒体库统计卡片
```yaml
type: glance
title: 媒体库统计
entities:
  - entity: sensor.moviepilot_movie_count
    name: 电影
  - entity: sensor.moviepilot_tv_count
    name: 剧集
  - entity: sensor.moviepilot_episode_count
    name: 集数
```

#### 下载监控卡片
```yaml
type: entities
title: MoviePilot 下载
entities:
  - entity: binary_sensor.moviepilot_downloading
    name: 下载状态
  - entity: sensor.moviepilot_downloader_speed
    name: 下载速度
  - entity: sensor.moviepilot_downloader_upload
    name: 上传速度
  - entity: sensor.moviepilot_total_downloaded
    name: 累计下载
```

#### 任务监控卡片
```yaml
type: entities
title: MoviePilot 任务
entities:
  - entity: binary_sensor.moviepilot_tasks_running
    name: 任务状态
  - entity: sensor.moviepilot_running_tasks
    name: 运行中
  - entity: sensor.moviepilot_pending_tasks
    name: 等待中
  - entity: button.moviepilot_refresh
    name: 刷新数据
```

### 自动化示例

#### 使用通知服务的自动化
```yaml
automation:
  - alias: "MoviePilot下载完成通知"
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

#### 磁盘空间监控通知
```yaml
automation:
  - alias: "MoviePilot磁盘空间警告"
    trigger:
      - platform: numeric_state
        entity_id: sensor.moviepilot_disk
        above: 90
    action:
      - service: notify.moviepilot
        data:
          title: "⚠️ 磁盘空间警告"
          message: >
            磁盘使用率已达 {{ states('sensor.moviepilot_disk') }}%
            可用空间: {{ states('sensor.moviepilot_disk_free') }}GB
          data:
            type: "System"
```

#### 每日媒体库统计
```yaml
automation:
  - alias: "每日MoviePilot统计"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - service: notify.mobile_app
        data:
          title: "MoviePilot每日统计"
          message: >
            今日媒体库状态：
            电影: {{ states('sensor.moviepilot_movie_count') }}部
            剧集: {{ states('sensor.moviepilot_tv_count') }}部
            总集数: {{ states('sensor.moviepilot_episode_count') }}集
```

---

## 🛠️ 技术细节

### 支持的API端点

本集成使用以下MoviePilot API v2端点（已验证可用）：

- `/api/v1/message/` - 连接测试
- `/api/v1/dashboard/cpu2` - CPU使用率
- `/api/v1/dashboard/memory2` - 内存使用率
- `/api/v1/dashboard/storage2` - 存储使用率
- `/api/v1/dashboard/network2` - 网络使用率
- `/api/v1/dashboard/statistic2` - 媒体库统计
- `/api/v1/dashboard/downloader2` - 下载器信息
- `/api/v1/dashboard/schedule2` - 计划任务
- `/api/v1/transfer/now` - 传输状态

### 认证方式

使用URL参数认证: `?token=your_api_token`

### 数据更新

- **默认更新间隔**: 30秒
- **可配置范围**: 10-300秒
- **并发请求**: 所有API端点并发请求，提高响应速度
- **错误处理**: 单个端点失败不影响其他数据

### 架构设计

```
moviepilot/
├── __init__.py          # 集成入口
├── const.py            # 常量定义
├── config_flow.py      # 配置流程
├── api.py              # API客户端
├── sensor.py           # 传感器平台 + Coordinator
├── binary_sensor.py    # 二进制传感器平台
├── button.py           # 按钮平台
└── manifest.json       # 集成元数据
```

---

## 🔧 故障排除

### 连接失败

**问题**: 无法连接到MoviePilot

**解决方案**:
1. 检查MoviePilot服务是否运行
2. 确认主机地址和端口正确
3. 检查防火墙设置
4. 查看Home Assistant日志: `设置 -> 系统 -> 日志`

### Token认证失败

**问题**: 401 Authentication Failed

**解决方案**:
1. 在MoviePilot中重新生成API Token
2. 确保token没有空格或特殊字符
3. 在集成配置中更新token

### 部分传感器无数据

**问题**: 某些传感器显示"不可用"

**解决方案**:
1. MoviePilot版本可能不支持某些API
2. 检查MoviePilot日志确认API正常
3. 尝试手动点击"刷新数据"按钮

### 更新频率过高

**问题**: 系统负载较高

**解决方案**:
1. 进入集成配置
2. 增加更新间隔至60秒或更长

---

## 📝 更新日志

### v1.0.0 (2025-10-08) - 首次发布
- 🔔 **通知服务** - 支持标准 notify.moviepilot 服务
- 📨 **增强通知功能** - 支持多种通知类型（Manual, System, Download, Transfer）
- 📖 **完整文档** - 包含 NOTIFICATION_GUIDE.md 通知使用指南
- 📊 **系统监控** - 10个传感器实时监控系统状态
- 🎬 **媒体库统计** - 监控电影、剧集数量
- ⬇️ **下载监控** - 实时下载速度和状态
- 📅 **任务监控** - 追踪运行中和等待中的任务
- 🔘 **二进制传感器** - 在线状态、任务运行、下载状态
- ✅ **HACS 合规** - 完全符合 HACS 标准
- 📄 **MIT 许可** - 开源友好

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 开发环境设置

```bash
git clone https://github.com/buynow2010/Moviepilot-HA
cd Moviepilot-HA
# 将moviepilot文件夹链接到Home Assistant
ln -s $(pwd)/moviepilot ~/.homeassistant/custom_components/
```

### 运行测试

```bash
# API端点测试
python3 moviepilot/test_api.py

# 查看测试结果
cat moviepilot/api_test_results.json
```

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🙏 致谢

- [MoviePilot](https://github.com/jxxghp/MoviePilot) - 优秀的媒体自动化工具
- [Home Assistant](https://www.home-assistant.io/) - 最好的开源智能家居平台
- 所有贡献者和用户

---

## 📞 支持

- **问题反馈**: [GitHub Issues](https://github.com/buynow2010/Moviepilot-HA/issues)
- **讨论交流**: [GitHub Discussions](https://github.com/buynow2010/Moviepilot-HA/discussions)
- **MoviePilot官方**: [MoviePilot 项目](https://github.com/jxxghp/MoviePilot)

---

## 📸 截图

*待添加实际截图*

---

**享受您的MoviePilot + Home Assistant集成体验！** 🎬🏠

# MoviePilot Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/buynow2010/Moviepilot-HA.svg)](https://github.com/buynow2010/Moviepilot-HA/releases)
[![License](https://img.shields.io/github/license/buynow2010/Moviepilot-HA.svg)](LICENSE)

将 MoviePilot 媒体自动化工具完美集成到 Home Assistant 中，实时监控媒体服务器状态、下载进度和系统资源。

**版本**: v1.0.0 | **发布日期**: 2025-10-08

---

## ✨ 主要特性

### 🔔 通知服务
- **notify.moviepilot** - 标准 Home Assistant 通知服务
- **moviepilot.send_notification** - 自定义通知服务
- 支持 4 种通知类型（Manual, System, Download, Transfer）

### 📊 系统监控
- **10 个传感器** - CPU、内存、磁盘、下载速度、任务、媒体库统计
- **3 个二进制传感器** - 在线状态、任务运行、下载状态
- 实时数据更新，30秒刷新间隔

### 🔌 完整 API 集成
- 支持 MoviePilot API v1
- 9 个验证可用的 API 端点
- 并发请求优化，快速响应

---

## 📦 安装

### 方法 1: 通过 HACS 安装（推荐）

1. 打开 HACS → 集成
2. 右上角菜单 → 自定义存储库
3. 添加仓库：`https://github.com/buynow2010/Moviepilot-HA`
4. 类别：Integration
5. 搜索并安装 "MoviePilot"
6. 重启 Home Assistant

### 方法 2: 手动安装

1. 下载最新 [Release](https://github.com/buynow2010/Moviepilot-HA/releases)
2. 解压并复制 `custom_components/moviepilot` 到你的 Home Assistant `config/custom_components/` 目录
3. 重启 Home Assistant

---

## ⚙️ 配置

1. 在 Home Assistant 中，进入 **设置** → **设备与服务**
2. 点击 **添加集成**
3. 搜索 **MoviePilot**
4. 输入配置信息：
   - **主机地址**: MoviePilot 服务器地址（如 `192.168.1.100`）
   - **端口**: 默认 `3000`
   - **API Token**: 从 MoviePilot 设置中获取

---

## 🚀 快速开始

### 发送通知

```yaml
# 标准通知服务（推荐）
service: notify.moviepilot
data:
  message: "电影下载完成"
  title: "MoviePilot"
  data:
    type: "Download"

# 自定义服务
service: moviepilot.send_notification
data:
  title: "磁盘空间警告"
  message: "剩余空间不足 100GB"
  type: "System"
```

### 自动化示例

```yaml
automation:
  - alias: "下载完成通知"
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

---

## 📖 文档

- 📘 [完整集成指南](docs/INTEGRATION_GUIDE.md) - 详细的功能说明和配置
- 🔔 [通知服务指南](docs/NOTIFICATION_GUIDE.md) - 通知功能详细文档
- 📝 [更新日志](docs/CHANGELOG_v1.0.0.md) - v1.0.0 发布说明
- 🛠️ [安装说明](docs/INSTALL.md) - 详细的安装步骤

---

## 🎯 HACS 合规

本集成完全符合 HACS 2025 标准：
- ✅ 标准目录结构
- ✅ Config Flow UI 配置
- ✅ 完整的 manifest.json
- ✅ 国际化支持
- ✅ MIT 开源许可

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发环境

```bash
git clone https://github.com/buynow2010/Moviepilot-HA
cd Moviepilot-HA
ln -s $(pwd)/custom_components/moviepilot ~/.homeassistant/custom_components/
```

---

## 📄 许可证

[MIT License](LICENSE) - 开源友好

---

## 🙏 致谢

- [MoviePilot](https://github.com/jxxghp/MoviePilot) - 优秀的媒体自动化工具
- [Home Assistant](https://www.home-assistant.io/) - 最好的智能家居平台

---

## 📞 支持

- 💬 [GitHub Issues](https://github.com/buynow2010/Moviepilot-HA/issues)
- 🗨️ [GitHub Discussions](https://github.com/buynow2010/Moviepilot-HA/discussions)
- 🎬 [MoviePilot 官方](https://github.com/jxxghp/MoviePilot)

---

**享受您的 MoviePilot + Home Assistant 集成体验！** 🎬🏠

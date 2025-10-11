# MoviePilot for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/buynow2010/Moviepilot-HA.svg)](https://github.com/buynow2010/Moviepilot-HA/releases)
[![License](https://img.shields.io/github/license/buynow2010/Moviepilot-HA.svg)](LICENSE)

将 MoviePilot 媒体管理平台无缝集成到 Home Assistant，实现系统监控与状态跟踪。

[English](README_EN.md) | 简体中文

## 🚀 快速开始

<table>
<tr>
<td align="center">
<a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=buynow2010&repository=Moviepilot-HA&category=integration">
<img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="添加HACS仓库" />
</a>
<br />
<strong>添加到 HACS</strong>
</td>
<td align="center">
<a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=moviepilot">
<img src="https://my.home-assistant.io/badges/config_flow_start.svg" alt="添加集成" />
</a>
<br />
<strong>添加集成</strong>
</td>
</tr>
</table>

## 功能特性

### 📊 监控传感器
- 系统监控：CPU、内存、磁盘使用率和可用空间
- 下载管理：下载速度
- 媒体统计：电影、剧集数量和用户统计
- 状态监控：下载状态

---

## 安装方式

### 方法一：通过 HACS 安装（推荐）

[![添加HACS仓库](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=buynow2010&repository=Moviepilot-HA&category=integration)

**一键安装（推荐）**：点击上方徽章，直接在 HACS 中添加此仓库

**手动添加**：
1. 确保已安装 [HACS](https://hacs.xyz/)
2. HACS → 集成 → 右上角菜单 → 自定义存储库
3. 输入: `https://github.com/buynow2010/Moviepilot-HA`
4. 类别: Integration → 添加
5. 搜索 "MoviePilot" → 下载
6. 重启 Home Assistant

### 方法二：手动安装

1. 下载 [最新版本](https://github.com/buynow2010/Moviepilot-HA/releases)
2. 解压到 `custom_components/moviepilot/`
3. 重启 Home Assistant

---

## 配置

### 1. 添加集成

[![添加集成](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=moviepilot)

**一键添加（推荐）**：点击上方徽章，直接跳转到添加集成页面

**手动添加**：**设置** → **设备与服务** → **添加集成** → 搜索 **MoviePilot**

配置信息：
- **主机**: MoviePilot 服务器地址（如 `192.168.1.100`）
- **端口**: 默认 `3000`
- **API Token**: 在 MoviePilot → 设置 → API 中获取

 

---

## 使用示例

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

### 传感器
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
 

### 二进制传感器（2个）
- `binary_sensor.moviepilot_online` - 在线状态
- `binary_sensor.moviepilot_downloading` - 下载状态

---

 

---

 

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

 

---

## 系统要求

- Home Assistant 2024.1.0+
- MoviePilot V2+
- Python 3.11+

---

## 更新日志

查看 [CHANGELOG.md](CHANGELOG.md)

---

## 支持与反馈

- **问题反馈**: [GitHub Issues](https://github.com/buynow2010/Moviepilot-HA/issues)
- **功能请求**: [GitHub Issues](https://github.com/buynow2010/Moviepilot-HA/issues)
- **讨论交流**: [GitHub Discussions](https://github.com/buynow2010/Moviepilot-HA/discussions)

## 友情链接

### 🏠 Home Assistant 中文网

[![Home Assistant 中文网](https://img.shields.io/badge/Home%20Assistant-中文网-blue?style=for-the-badge&logo=home-assistant)](https://www.hasscn.top)

[**Home Assistant 中文网 (hasscn.top)**](https://www.hasscn.top) - 最全面的免费 Home Assistant 中文站点，提供：
- 🚀 **Home Assistant OS 极速版** - 专为中国优化的加速版系统
- ⚡ **HACS 极速版** - 使用国内镜像加速插件下载
- 📚 **中文文档教程** - 详细的安装配置指南
- 💬 **社区支持** - 微信公众号：老王杂谈说

**特别适合国内用户使用，解决下载慢、连接困难等问题！**

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 致谢

- [MoviePilot](https://github.com/jxxghp/MoviePilot) - 强大的媒体管理平台
- [Home Assistant](https://www.home-assistant.io/) - 开源智能家居平台
- [HACS](https://hacs.xyz/) - Home Assistant 社区商店

---

**Made with ❤️ for Home Assistant Community**

# MoviePilot Home Assistant 集成 v1.0.0 - 发布说明

## 🎉 首次正式发布

MoviePilot Home Assistant 集成现已正式发布！这是一个功能完整、符合 HACS 标准的集成，可以将 MoviePilot 媒体自动化工具完美集成到 Home Assistant 中。

---

## ✨ 核心功能

### 1. 通知服务 🔔

#### 通知平台：
- **notify.py** - 完整的 Home Assistant 标准通知平台
  - 支持 `notify.moviepilot` 服务
  - 完全兼容 HA 通知规范
  - 支持 title、message、data 参数

#### 通知类型：
- **Manual** - 手动触发的通知（默认）
- **System** - 系统状态、警告等
- **Download** - 下载相关通知
- **Transfer** - 文件整理、转移相关

### 2. 系统监控 📊

**10 个传感器**实时监控：
- CPU 使用率
- 内存使用率
- 磁盘使用率 / 可用空间
- 下载速度
- 运行中任务数
- 电影 / 剧集 / 集数 / 用户数量

### 3. 二进制传感器 🔘

**3 个状态传感器**：
- 在线状态
- 有任务运行
- 下载中

---

## 🚀 使用方式

### 标准 Notify 服务（推荐）
```yaml
action:
  - service: notify.moviepilot
    data:
      title: "下载完成"
      message: "电影《流浪地球2》已下载完成"
      data:
        type: "Download"
```

### 自定义服务
```yaml
action:
  - service: moviepilot.send_notification
    data:
      title: "磁盘空间警告"
      message: "剩余空间不足 100GB"
      type: "System"
```

---

## 📋 HACS 合规性

### 完全符合 HACS 2025 标准 ✅
- ✅ manifest.json - 包含所有必需字段
- ✅ hacs.json - 正确配置 domains
- ✅ README.md - 详细使用说明
- ✅ LICENSE - MIT 开源许可
- ✅ 完整的平台实现 - sensor, binary_sensor, notify
- ✅ 配置流程 - UI 配置支持
- ✅ 国际化 - strings.json

---

## 📖 文档

### 包含文档：
- **README.md** - 完整的安装和使用指南
- **NOTIFICATION_GUIDE.md** - 详细的通知服务使用指南
- **INSTALL.md** - 安装说明

---

## 🎯 安装方法

### 方法 1: HACS 安装（推荐）

1. 打开 HACS → 集成
2. 右上角菜单 → 自定义存储库
3. 添加: `https://github.com/buynow2010/Moviepilot-HA`
4. 类别: Integration
5. 搜索安装 "MoviePilot"
6. 重启 Home Assistant

### 方法 2: 手动安装

1. 下载仓库
2. 复制 `moviepilot` 到 `config/custom_components/`
3. 重启 Home Assistant

---

## 🙏 致谢

- [MoviePilot](https://github.com/jxxghp/MoviePilot) - 优秀的媒体自动化工具
- [Home Assistant](https://www.home-assistant.io/) - 最好的智能家居平台

---

**享受您的 MoviePilot + Home Assistant 集成体验！** 🎬🏠

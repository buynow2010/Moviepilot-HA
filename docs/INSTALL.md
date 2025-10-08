# 安装指南

## 快速安装

```bash
# 从项目目录
cd /Users/buynow/claude/moviepilot-Project
cp -r moviepilot ~/.homeassistant/custom_components/
```

重启Home Assistant后：
1. **设置 -> 设备与服务 -> 添加集成**
2. 搜索 **MoviePilot**
3. 输入配置信息

## 配置参数

- **主机**: MoviePilot服务器地址
- **端口**: `3000` (默认)
- **API Token**: 从MoviePilot获取

## 验证安装

检查文件：
```bash
ls ~/.homeassistant/custom_components/moviepilot/manifest.json
```

查看实体（应该有24个）：
```
开发者工具 -> 状态 -> 搜索 "moviepilot"
```

## 故障排除

### 找不到集成
- 确认文件路径正确
- 重启Home Assistant

### 认证失败
- 检查Token是否正确
- 在MoviePilot重新生成token

### 实体无数据
- 确认MoviePilot正在运行
- 点击 `button.moviepilot_test_connection`
- 查看HA日志

## 详细文档

完整使用手册请查看: `README.md`

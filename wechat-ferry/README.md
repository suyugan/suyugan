# WeChatFerry 群消息采集方案

## 概述
使用 WeChatFerry (wcferry) Hook 微信 PC 客户端，自动采集群聊消息并同步到腾讯云服务器。

## 环境要求
- **微信版本**: 3.9.12.51（已安装在 D:\WeChat）
- **Python**: 3.8+
- **wcferry**: 39.5.2.0（适配微信 3.9.x）
- **操作系统**: Windows（WeChatFerry 仅支持 Windows）

## 文件说明
| 文件 | 说明 |
|------|------|
| `config.py` | 配置文件（数据库路径、监听群、服务器信息） |
| `collector.py` | 消息采集脚本（核心） |
| `sync.py` | 同步脚本（上传到腾讯云） |
| `viewer.py` | 查看工具（查看已采集的消息） |
| `requirements.txt` | Python 依赖 |

## 快速启动

### 1. 安装依赖
```powershell
cd C:\Users\Administrator\.openclaw\workspace\wechat-ferry
pip install -r requirements.txt
```

### 2. 确保微信已登录
- 打开 D:\WeChat 里的微信
- 确认已登录且版本为 3.9.12.51

### 3. 启动采集器
```powershell
python collector.py
```

启动后会：
1. 连接微信（注入 DLL）
2. 打印登录账号信息
3. **打印所有群聊列表**（包含 roomid）
4. 开始监听消息

### 4. 配置监听群（可选）
查看启动日志中的群列表，找到目标群的 roomid，编辑 `config.py`：
```python
WATCH_ROOMS = ["12345678@chatroom", "87654321@chatroom"]
```
留空 `[]` 则监听所有群。

### 5. 启动同步（另开终端）
```powershell
# 持续同步（每5分钟）
python sync.py

# 或只同步一次
python sync.py --once
```

### 6. 查看数据
```powershell
# 查看统计
python viewer.py stats

# 查看群列表
python viewer.py rooms

# 查看最近消息
python viewer.py messages

# 查看指定群消息
python viewer.py messages --room 12345678@chatroom --limit 100
```

## 数据存储
- **本地数据库**: `wechat-ferry/messages.db`（SQLite）
- **本地图片**: `wechat-ferry/images/`
- **远程数据库**: `/home/ubuntu/wechat-messages/messages.db`
- **远程图片**: `/home/ubuntu/wechat-messages/images/`

## 消息类型支持
| 类型码 | 说明 | 存储内容 |
|--------|------|----------|
| 1 | 文本 | content 字段 |
| 3 | 图片 | 自动下载到 images/ |
| 34 | 语音 | xml 字段 |
| 43 | 视频 | thumb 缩略图路径 |
| 47 | 表情 | xml 字段 |
| 49 | 链接/文件/小程序 | xml 字段含完整信息 |
| 10000 | 系统消息 | content 字段 |

## 注意事项
⚠️ **WeChatFerry 会注入微信进程的 DLL**，使用前请了解风险。
⚠️ 采集器运行时不要关闭微信。
⚠️ 微信版本必须是 3.9.12.51，其他版本可能不兼容。
⚠️ 首次启动需要**以管理员权限运行**。

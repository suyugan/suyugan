"""WeChatFerry 群消息采集 - 配置文件"""

import os

# ============ 本地配置 ============

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), "messages.db")

# 图片保存目录
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images")

# 要监听的群聊 roomid 列表（留空则监听所有群）
# 群 roomid 格式: 数字@chatroom，例如 "12345678@chatroom"
# 启动后会打印所有群列表，找到目标群的 roomid 填在这里
WATCH_ROOMS = []

# ============ 腾讯云服务器配置 ============

REMOTE_HOST = "106.55.158.137"
REMOTE_USER = "ubuntu"
REMOTE_PASSWORD = "REDACTED_SERVER_PWD"
REMOTE_DB_PATH = "/home/ubuntu/wechat-messages/messages.db"
REMOTE_IMAGE_DIR = "/home/ubuntu/wechat-messages/images"

# 同步间隔（秒）
SYNC_INTERVAL = 300  # 5分钟

# ============ wechat-viewer API ============

WECHAT_VIEWER_API = "http://bm.weiixxin.com/wechat/api"

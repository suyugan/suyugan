"""WeChatFerry 群消息采集脚本

功能：
- 监听指定群聊消息
- 保存到本地 SQLite 数据库
- 支持文本、图片、链接等消息类型
- 自动下载图片到本地
"""

import os
import sys
import time
import json
import signal
import sqlite3
import logging
from datetime import datetime
from queue import Empty

from wcferry import Wcf, WxMsg

from config import DB_PATH, IMAGE_DIR, WATCH_ROOMS

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            os.path.join(os.path.dirname(__file__), "collector.log"),
            encoding="utf-8",
        ),
    ],
)
LOG = logging.getLogger("collector")

# 消息类型映射
MSG_TYPES = {
    1: "文本",
    3: "图片",
    34: "语音",
    42: "名片",
    43: "视频",
    47: "表情",
    48: "位置",
    49: "链接/文件/小程序",
    10000: "系统消息",
    10002: "撤回消息",
}


def init_db():
    """初始化数据库"""
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            msg_id TEXT UNIQUE,
            type INTEGER,
            type_name TEXT,
            roomid TEXT,
            sender TEXT,
            sender_name TEXT,
            content TEXT,
            xml TEXT,
            thumb TEXT,
            extra TEXT,
            image_path TEXT,
            ts INTEGER,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            synced INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            wxid TEXT PRIMARY KEY,
            name TEXT,
            remark TEXT,
            updated_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chatrooms (
            roomid TEXT PRIMARY KEY,
            name TEXT,
            members TEXT,
            updated_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_roomid ON messages(roomid)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_synced ON messages(synced)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_ts ON messages(ts)")
    conn.commit()
    conn.close()
    LOG.info(f"数据库已初始化: {DB_PATH}")


def save_message(msg: WxMsg, wcf: Wcf, sender_name: str = ""):
    """保存消息到数据库"""
    conn = sqlite3.connect(DB_PATH)
    try:
        type_name = MSG_TYPES.get(msg.type, f"未知({msg.type})")
        image_path = ""

        # 下载图片
        if msg.type == 3 and hasattr(msg, "extra") and msg.extra:
            try:
                os.makedirs(IMAGE_DIR, exist_ok=True)
                img_path = wcf.download_image(msg.id, msg.extra, IMAGE_DIR, timeout=30)
                if img_path:
                    image_path = img_path
                    LOG.info(f"图片已下载: {img_path}")
            except Exception as e:
                LOG.warning(f"图片下载失败: {e}")

        conn.execute(
            """INSERT OR IGNORE INTO messages 
               (msg_id, type, type_name, roomid, sender, sender_name, content, xml, thumb, extra, image_path, ts)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                str(msg.id),
                msg.type,
                type_name,
                msg.roomid or "",
                msg.sender,
                sender_name,
                msg.content,
                msg.xml or "",
                msg.thumb or "",
                getattr(msg, "extra", "") or "",
                image_path,
                getattr(msg, "ts", int(time.time())),
            ),
        )
        conn.commit()
        LOG.info(
            f"[{type_name}] {msg.roomid or '私聊'} | {sender_name}({msg.sender}): "
            f"{msg.content[:80] if msg.content else '<无文本>'}"
        )
    except sqlite3.IntegrityError:
        pass  # 重复消息
    except Exception as e:
        LOG.error(f"保存消息失败: {e}")
    finally:
        conn.close()


def cache_contacts(wcf: Wcf):
    """缓存联系人到数据库"""
    contacts = wcf.get_contacts()
    conn = sqlite3.connect(DB_PATH)
    for c in contacts:
        conn.execute(
            "INSERT OR REPLACE INTO contacts (wxid, name, remark, updated_at) VALUES (?, ?, ?, datetime('now','localtime'))",
            (c.get("wxid", ""), c.get("name", ""), c.get("remark", "")),
        )
    conn.commit()
    conn.close()
    LOG.info(f"已缓存 {len(contacts)} 个联系人")
    return {c.get("wxid", ""): c.get("remark") or c.get("name", "") for c in contacts}


def cache_chatrooms(wcf: Wcf, contacts_map: dict):
    """缓存群信息"""
    conn = sqlite3.connect(DB_PATH)
    rooms = [c for c in wcf.get_contacts() if c.get("wxid", "").endswith("@chatroom")]
    for r in rooms:
        roomid = r.get("wxid", "")
        name = r.get("remark") or r.get("name", "")
        try:
            members = wcf.get_chatroom_members(roomid)
            members_json = json.dumps(members, ensure_ascii=False)
        except:
            members_json = "{}"
        conn.execute(
            "INSERT OR REPLACE INTO chatrooms (roomid, name, members, updated_at) VALUES (?, ?, ?, datetime('now','localtime'))",
            (roomid, name, members_json),
        )
    conn.commit()
    conn.close()
    LOG.info(f"已缓存 {len(rooms)} 个群聊:")
    for r in rooms:
        LOG.info(f"  {r.get('wxid')}: {r.get('remark') or r.get('name')}")
    return rooms


def get_sender_name(wcf: Wcf, msg: WxMsg, contacts_map: dict) -> str:
    """获取发送者名称"""
    if msg.sender in contacts_map:
        return contacts_map[msg.sender]
    # 尝试获取群名片
    if msg.roomid:
        try:
            alias = wcf.get_alias_in_chatroom(msg.sender, msg.roomid)
            if alias:
                return alias
        except:
            pass
    # 尝试查询
    try:
        info = wcf.get_info_by_wxid(msg.sender)
        name = info.get("name", msg.sender)
        contacts_map[msg.sender] = name
        return name
    except:
        return msg.sender


def main():
    LOG.info("=" * 50)
    LOG.info("WeChatFerry 群消息采集器启动中...")
    LOG.info("=" * 50)

    # 初始化数据库
    init_db()

    # 启动 WCF
    LOG.info("正在连接微信...")
    wcf = Wcf(block=True)

    if not wcf.is_login():
        LOG.error("微信未登录！请先登录微信。")
        return

    # 获取登录信息
    user_info = wcf.get_user_info()
    LOG.info(f"已登录: {user_info.get('name', '?')} ({wcf.get_self_wxid()})")

    # 缓存联系人和群
    contacts_map = cache_contacts(wcf)
    rooms = cache_chatrooms(wcf, contacts_map)

    if WATCH_ROOMS:
        LOG.info(f"监听群聊: {WATCH_ROOMS}")
    else:
        LOG.info("监听所有群聊消息")

    # 开始接收消息
    wcf.enable_receiving_msg()
    LOG.info("消息接收已启动，按 Ctrl+C 停止")

    running = True

    def on_exit(sig, frame):
        nonlocal running
        running = False
        LOG.info("正在停止...")

    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)

    while running:
        try:
            msg = wcf.get_msg(block=True)
        except Empty:
            continue
        except Exception as e:
            LOG.error(f"获取消息异常: {e}")
            time.sleep(1)
            continue

        # 只处理群消息
        if not msg.from_group():
            continue

        # 过滤群
        if WATCH_ROOMS and msg.roomid not in WATCH_ROOMS:
            continue

        # 跳过自己发的
        if msg.from_self():
            continue

        sender_name = get_sender_name(wcf, msg, contacts_map)
        save_message(msg, wcf, sender_name)

    # 清理
    wcf.cleanup()
    LOG.info("采集器已停止")


if __name__ == "__main__":
    main()

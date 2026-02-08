"""查看工具 - 查看已采集的消息"""

import os
import sys
import sqlite3
import argparse
from datetime import datetime

from config import DB_PATH


def list_rooms():
    """列出所有群聊"""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT roomid, name FROM chatrooms ORDER BY name
    """).fetchall()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"{'群ID':<30} {'群名称'}")
    print(f"{'='*60}")
    for roomid, name in rows:
        print(f"{roomid:<30} {name}")
    print(f"\n共 {len(rows)} 个群")


def list_messages(roomid=None, limit=50):
    """列出消息"""
    conn = sqlite3.connect(DB_PATH)
    if roomid:
        rows = conn.execute(
            "SELECT ts, type_name, sender_name, content FROM messages WHERE roomid=? ORDER BY ts DESC LIMIT ?",
            (roomid, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT ts, roomid, type_name, sender_name, content FROM messages ORDER BY ts DESC LIMIT ?",
            (limit,)
        ).fetchall()
    conn.close()

    rows.reverse()
    print(f"\n最近 {len(rows)} 条消息:")
    print("-" * 80)
    for row in rows:
        if roomid:
            ts, type_name, sender, content = row
            ts_str = datetime.fromtimestamp(ts).strftime("%m-%d %H:%M")
            content_short = (content or "")[:60].replace("\n", " ")
            print(f"[{ts_str}] [{type_name}] {sender}: {content_short}")
        else:
            ts, rid, type_name, sender, content = row
            ts_str = datetime.fromtimestamp(ts).strftime("%m-%d %H:%M")
            content_short = (content or "")[:50].replace("\n", " ")
            print(f"[{ts_str}] {rid} [{type_name}] {sender}: {content_short}")


def stats():
    """统计信息"""
    conn = sqlite3.connect(DB_PATH)
    total = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    synced = conn.execute("SELECT COUNT(*) FROM messages WHERE synced=1").fetchone()[0]
    unsynced = total - synced
    rooms = conn.execute("SELECT COUNT(DISTINCT roomid) FROM messages WHERE roomid != ''").fetchone()[0]
    contacts = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
    conn.close()

    print(f"\n📊 采集统计:")
    print(f"  总消息数: {total}")
    print(f"  已同步:   {synced}")
    print(f"  待同步:   {unsynced}")
    print(f"  群聊数:   {rooms}")
    print(f"  联系人:   {contacts}")


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("数据库不存在，请先运行 collector.py")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="查看采集数据")
    parser.add_argument("action", choices=["rooms", "messages", "stats"], help="操作")
    parser.add_argument("--room", help="群ID")
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    if args.action == "rooms":
        list_rooms()
    elif args.action == "messages":
        list_messages(args.room, args.limit)
    elif args.action == "stats":
        stats()

"""同步脚本 - 将本地采集的消息上传到腾讯云服务器

使用 paramiko (SSH/SFTP) 将本地 SQLite 数据库和图片同步到远程服务器。
也支持通过 wechat-viewer API 上传。
"""

import os
import sys
import time
import json
import sqlite3
import logging
import argparse
from datetime import datetime

import paramiko
from scp import SCPClient

from config import (
    DB_PATH, IMAGE_DIR,
    REMOTE_HOST, REMOTE_USER, REMOTE_PASSWORD,
    REMOTE_DB_PATH, REMOTE_IMAGE_DIR,
    SYNC_INTERVAL, WECHAT_VIEWER_API,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            os.path.join(os.path.dirname(__file__), "sync.log"),
            encoding="utf-8",
        ),
    ],
)
LOG = logging.getLogger("sync")


def get_ssh_client():
    """创建 SSH 连接"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(REMOTE_HOST, username=REMOTE_USER, password=REMOTE_PASSWORD, timeout=10)
    return client


def ensure_remote_dirs(ssh):
    """确保远程目录存在"""
    for d in [os.path.dirname(REMOTE_DB_PATH), REMOTE_IMAGE_DIR]:
        ssh.exec_command(f"mkdir -p {d}")


def sync_db(ssh):
    """同步数据库文件到远程"""
    if not os.path.exists(DB_PATH):
        LOG.warning("本地数据库不存在，跳过同步")
        return 0

    # 导出未同步的消息为 JSON
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM messages WHERE synced = 0 ORDER BY ts").fetchall()
    
    if not rows:
        LOG.info("没有新消息需要同步")
        conn.close()
        return 0

    messages = [dict(r) for r in rows]
    msg_ids = [m["msg_id"] for m in messages]
    
    # 上传 JSON 到远程并导入
    json_data = json.dumps(messages, ensure_ascii=False, default=str)
    
    # 写入临时文件
    tmp_path = "/tmp/wcf_sync.json"
    sftp = ssh.open_sftp()
    with sftp.file(tmp_path, "w") as f:
        f.write(json_data)
    
    # 远程执行导入脚本
    import_script = f"""
import json, sqlite3, os
os.makedirs(os.path.dirname('{REMOTE_DB_PATH}'), exist_ok=True)
conn = sqlite3.connect('{REMOTE_DB_PATH}')
conn.execute('''CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    msg_id TEXT UNIQUE, type INTEGER, type_name TEXT,
    roomid TEXT, sender TEXT, sender_name TEXT,
    content TEXT, xml TEXT, thumb TEXT, extra TEXT,
    image_path TEXT, ts INTEGER,
    created_at TEXT, synced INTEGER DEFAULT 1
)''')
with open('{tmp_path}') as f:
    msgs = json.load(f)
count = 0
for m in msgs:
    try:
        conn.execute(
            'INSERT OR IGNORE INTO messages (msg_id,type,type_name,roomid,sender,sender_name,content,xml,thumb,extra,image_path,ts,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (m['msg_id'],m['type'],m['type_name'],m['roomid'],m['sender'],m['sender_name'],m['content'],m['xml'],m['thumb'],m['extra'],m.get('image_path',''),m['ts'],m['created_at'])
        )
        count += 1
    except Exception as e:
        pass
conn.commit()
conn.close()
print(f'导入 {{count}} 条消息')
"""
    sftp.file("/tmp/wcf_import.py", "w").write(import_script)
    sftp.close()
    
    _, stdout, stderr = ssh.exec_command("python3 /tmp/wcf_import.py")
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out:
        LOG.info(f"远程导入: {out.strip()}")
    if err:
        LOG.warning(f"远程错误: {err.strip()}")

    # 标记已同步
    placeholders = ",".join(["?"] * len(msg_ids))
    conn.execute(f"UPDATE messages SET synced = 1 WHERE msg_id IN ({placeholders})", msg_ids)
    conn.commit()
    conn.close()

    LOG.info(f"已同步 {len(messages)} 条消息")
    return len(messages)


def sync_images(ssh):
    """同步图片到远程"""
    if not os.path.exists(IMAGE_DIR):
        return 0

    local_images = set(os.listdir(IMAGE_DIR))
    if not local_images:
        return 0

    ensure_remote_dirs(ssh)
    
    # 获取远程已有的图片
    _, stdout, _ = ssh.exec_command(f"ls {REMOTE_IMAGE_DIR} 2>/dev/null || echo ''")
    remote_images = set(stdout.read().decode().split())
    
    # 找出需要上传的
    to_upload = local_images - remote_images
    if not to_upload:
        LOG.info("没有新图片需要同步")
        return 0

    with SCPClient(ssh.get_transport()) as scp:
        for img in to_upload:
            local_path = os.path.join(IMAGE_DIR, img)
            remote_path = f"{REMOTE_IMAGE_DIR}/{img}"
            try:
                scp.put(local_path, remote_path)
                LOG.info(f"已上传图片: {img}")
            except Exception as e:
                LOG.warning(f"上传图片失败 {img}: {e}")

    LOG.info(f"已上传 {len(to_upload)} 张图片")
    return len(to_upload)


def sync_contacts(ssh):
    """同步联系人和群信息"""
    if not os.path.exists(DB_PATH):
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    contacts = [dict(r) for r in conn.execute("SELECT * FROM contacts").fetchall()]
    chatrooms = [dict(r) for r in conn.execute("SELECT * FROM chatrooms").fetchall()]
    conn.close()

    data = json.dumps({"contacts": contacts, "chatrooms": chatrooms}, ensure_ascii=False, default=str)
    
    sftp = ssh.open_sftp()
    with sftp.file("/tmp/wcf_contacts.json", "w") as f:
        f.write(data)

    import_script = f"""
import json, sqlite3, os
os.makedirs(os.path.dirname('{REMOTE_DB_PATH}'), exist_ok=True)
conn = sqlite3.connect('{REMOTE_DB_PATH}')
conn.execute('CREATE TABLE IF NOT EXISTS contacts (wxid TEXT PRIMARY KEY, name TEXT, remark TEXT, updated_at TEXT)')
conn.execute('CREATE TABLE IF NOT EXISTS chatrooms (roomid TEXT PRIMARY KEY, name TEXT, members TEXT, updated_at TEXT)')
with open('/tmp/wcf_contacts.json') as f:
    data = json.load(f)
for c in data['contacts']:
    conn.execute('INSERT OR REPLACE INTO contacts VALUES (?,?,?,?)', (c['wxid'],c['name'],c['remark'],c['updated_at']))
for r in data['chatrooms']:
    conn.execute('INSERT OR REPLACE INTO chatrooms VALUES (?,?,?,?)', (r['roomid'],r['name'],r['members'],r['updated_at']))
conn.commit()
conn.close()
print(f"联系人: {{len(data['contacts'])}}, 群: {{len(data['chatrooms'])}}")
"""
    sftp.file("/tmp/wcf_import_contacts.py", "w").write(import_script)
    sftp.close()

    _, stdout, stderr = ssh.exec_command("python3 /tmp/wcf_import_contacts.py")
    out = stdout.read().decode()
    if out:
        LOG.info(f"远程同步联系人: {out.strip()}")


def sync_once():
    """执行一次同步"""
    LOG.info("开始同步...")
    try:
        ssh = get_ssh_client()
        ensure_remote_dirs(ssh)
        
        msg_count = sync_db(ssh)
        img_count = sync_images(ssh)
        sync_contacts(ssh)
        
        ssh.close()
        LOG.info(f"同步完成: {msg_count} 条消息, {img_count} 张图片")
        return True
    except Exception as e:
        LOG.error(f"同步失败: {e}")
        return False


def sync_loop():
    """持续同步循环"""
    LOG.info(f"同步服务启动，间隔 {SYNC_INTERVAL} 秒")
    while True:
        sync_once()
        time.sleep(SYNC_INTERVAL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WeChatFerry 消息同步工具")
    parser.add_argument("--once", action="store_true", help="只同步一次")
    args = parser.parse_args()

    if args.once:
        sync_once()
    else:
        sync_loop()

#!/usr/bin/env python3
import paramiko
import json

HOST = "106.55.158.137"
USER = "ubuntu"
PASS = "REDACTED_SERVER_PWD"
APPID = "wx9a447fddc9ba6a59"
APPSECRET = "REDACTED_WECHAT_SECRET"

# Read local files
with open(r"C:\Users\Administrator\.openclaw\workspace\wechat-temp\article.html", "r", encoding="utf-8") as f:
    article_html = f.read()
with open(r"C:\Users\Administrator\.openclaw\workspace\wechat-temp\cover.jpg", "rb") as f:
    cover_bytes = f.read()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS)

# Upload files
sftp = ssh.open_sftp()
sftp.put(r"C:\Users\Administrator\.openclaw\workspace\wechat-temp\article.html", "/tmp/article.html")
sftp.put(r"C:\Users\Administrator\.openclaw\workspace\wechat-temp\cover.jpg", "/tmp/cover.jpg")

# Write a minimal publish script with ASCII-only Python, using json for strings
config = {
    "appid": APPID,
    "appsecret": APPSECRET,
    "title": "AI狂飙2026：六大趋势",
    "author": "",
    "digest": "AI行业正在发生什么？普通人如何应对？"
}

with sftp.open("/tmp/wx_config.json", "wb") as f:
    f.write(json.dumps(config, ensure_ascii=False).encode("utf-8"))

script = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, json, sys

with open("/tmp/wx_config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

APPID = cfg["appid"]
APPSECRET = cfg["appsecret"]

r = requests.get(f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}")
token = r.json().get("access_token")
if not token:
    print(f"Token error: {r.json()}")
    sys.exit(1)
print(f"Token OK")

# Upload cover
url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
with open("/tmp/cover.jpg", "rb") as f:
    r = requests.post(url, files={"media": ("cover.jpg", f, "image/jpeg")})
thumb_id = r.json().get("media_id")
if not thumb_id:
    print(f"Upload error: {r.json()}")
    sys.exit(1)
print(f"Cover uploaded: {thumb_id}")

# Read article
with open("/tmp/article.html", "r", encoding="utf-8") as f:
    content = f.read()

# Create draft
url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
data = {
    "articles": [{
        "title": cfg["title"],
        "author": cfg["author"],
        "digest": cfg["digest"],
        "content": content,
        "thumb_media_id": thumb_id,
        "content_source_url": "",
        "need_open_comment": 0
    }]
}
print(f"Title bytes: {len(cfg['title'].encode('utf-8'))}, Author bytes: {len(cfg['author'].encode('utf-8'))}, Digest bytes: {len(cfg['digest'].encode('utf-8'))}")
print(f"Title: [{cfg['title']}] Author: [{cfg['author']}] Digest: [{cfg['digest']}]")
r = requests.post(url, json=data)
result = r.json()
print(f"Draft: {json.dumps(result, ensure_ascii=False)}")

if "media_id" in result:
    media_id = result["media_id"]
    url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={token}"
    r = requests.post(url, json={"media_id": media_id})
    print(f"Publish: {json.dumps(r.json(), ensure_ascii=False)}")
else:
    print("FAILED")
'''

with sftp.open("/tmp/wx_publish2.py", "wb") as f:
    f.write(script.encode("utf-8"))
sftp.close()

stdin, stdout, stderr = ssh.exec_command("cd /tmp && python3 wx_publish2.py")
print("OUT:", stdout.read().decode())
err = stderr.read().decode()
if err:
    print("ERR:", err)
ssh.close()

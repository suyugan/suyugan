#!/usr/bin/env python3
"""Upload files to remote server and run publish script there."""
import paramiko
import os
import json
import base64

HOST = "106.55.158.137"
USER = "ubuntu"
PASS = "REDACTED_SERVER_PWD"
APPID = "wx9a447fddc9ba6a59"
APPSECRET = "REDACTED_WECHAT_SECRET"

# Read local files
article_path = r"C:\Users\Administrator\.openclaw\workspace\wechat-temp\article.html"
cover_path = r"C:\Users\Administrator\.openclaw\workspace\wechat-temp\cover.jpg"

with open(article_path, "r", encoding="utf-8") as f:
    article_html = f.read()
with open(cover_path, "rb") as f:
    cover_bytes = f.read()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS)

sftp = ssh.open_sftp()
sftp.put(article_path, "/tmp/article.html")
sftp.put(cover_path, "/tmp/cover.jpg")
sftp.close()

# Write publish script on remote
publish_script = '''#!/usr/bin/env python3
import requests, json, sys

APPID = "{appid}"
APPSECRET = "{appsecret}"

def get_token():
    r = requests.get(f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={{APPID}}&secret={{APPSECRET}}")
    d = r.json()
    if "access_token" not in d:
        print(f"Token error: {{d}}")
        sys.exit(1)
    return d["access_token"]

def upload_image(token, path):
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={{token}}&type=image"
    with open(path, "rb") as f:
        r = requests.post(url, files={{"media": ("cover.jpg", f, "image/jpeg")}})
    d = r.json()
    if "media_id" not in d:
        print(f"Upload error: {{d}}")
        sys.exit(1)
    return d["media_id"]

def create_draft(token, title, author, digest, content, thumb_media_id):
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={{token}}"
    data = {{
        "articles": [{{
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "thumb_media_id": thumb_media_id,
            "content_source_url": "",
            "need_open_comment": 0
        }}]
    }}
    r = requests.post(url, json=data)
    return r.json()

def free_publish(token, media_id):
    url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={{token}}"
    r = requests.post(url, json={{"media_id": media_id}})
    return r.json()

token = get_token()
print(f"Got token: {{token[:20]}}...")

thumb_id = upload_image(token, "/tmp/cover.jpg")
print(f"Uploaded cover: {{thumb_id}}")

with open("/tmp/article.html", "r") as f:
    content = f.read()

title = "AI\u72c2\u98d82026\uff1a\u516d\u5927\u8d8b\u52bf"
author = "\u82cf\u7164\u6dfe"
digest = "AI\u884c\u4e1a\u6b63\u5728\u53d1\u751f\u4ec0\u4e48\uff1f\u666e\u901a\u4eba\u8be5\u5982\u4f55\u5e94\u5bf9\uff1f"

result = create_draft(token, title, author, digest, content, thumb_id)
print(f"Draft result: {{json.dumps(result, ensure_ascii=False)}}")

if "media_id" in result:
    media_id = result["media_id"]
    pub = free_publish(token, media_id)
    print(f"Publish result: {{json.dumps(pub, ensure_ascii=False)}}")
else:
    print("Failed to create draft")
'''.format(appid=APPID, appsecret=APPSECRET)

# Write script via sftp instead to preserve encoding
sftp2 = ssh.open_sftp()
with sftp2.open("/tmp/wx_publish.py", "wb") as f:
    f.write(publish_script.encode("utf-8"))
sftp2.close()

stdin, stdout, stderr = ssh.exec_command("cd /tmp && python3 wx_publish.py")
out = stdout.read().decode()
err = stderr.read().decode()
print("STDOUT:", out)
if err:
    print("STDERR:", err)

ssh.close()

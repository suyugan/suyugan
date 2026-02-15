#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接在本地调用微信公众号API，不走SSH，避免编码问题"""
import requests
import json
import sys
import os

APPID = "wx9a447fddc9ba6a59"
APPSECRET = "REDACTED_WECHAT_SECRET"

ARTICLE_PATH = os.path.join(os.path.dirname(__file__), "article.html")
COVER_PATH = os.path.join(os.path.dirname(__file__), "cover.jpg")

def get_token():
    r = requests.get(f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}")
    d = r.json()
    if "access_token" not in d:
        print(f"Token error: {d}")
        sys.exit(1)
    print(f"Got token: {d['access_token'][:20]}...")
    return d["access_token"]

def upload_image(token, path):
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
    with open(path, "rb") as f:
        r = requests.post(url, files={"media": ("cover.jpg", f, "image/jpeg")})
    d = r.json()
    if "media_id" not in d:
        print(f"Upload error: {d}")
        sys.exit(1)
    print(f"Uploaded cover: {d['media_id']}")
    return d["media_id"]

def create_draft(token, title, author, digest, content, thumb_media_id):
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    data = {
        "articles": [{
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "thumb_media_id": thumb_media_id,
            "content_source_url": "",
            "need_open_comment": 0
        }]
    }
    r = requests.post(url, json=data)
    return r.json()

# Main
token = get_token()
thumb_id = upload_image(token, COVER_PATH)

with open(ARTICLE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

print(f"Article length: {len(content)} chars")
print(f"First 100 chars: {content[:100]}")

title = "AI狂飙2026：六大趋势"
author = "苏煜淦"
digest = "AI行业正在发生什么？普通人该如何应对？"

result = create_draft(token, title, author, digest, content, thumb_id)
print(f"Draft result: {json.dumps(result, ensure_ascii=False)}")

if "media_id" in result:
    print(f"\nSUCCESS! Draft created. media_id: {result['media_id']}")
    print("Please check drafts in WeChat admin panel")
else:
    print(f"\nFAILED: {result}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, urllib.request

APPID='wx9a447fddc9ba6a59'
APPSECRET='REDACTED_WECHAT_SECRET'

req0 = urllib.request.urlopen(f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}')
token = json.loads(req0.read())['access_token']

media_id = 'JAVwqK3hw2v25Dj8_tpgfElH1g0TJmVdO0-VyqSVqAsJ-xaZvnvI3zJ6pczdKvAF'
body1 = json.dumps({'media_id': media_id}).encode('utf-8')
req1 = urllib.request.Request(f'https://api.weixin.qq.com/cgi-bin/draft/get?access_token={token}', data=body1, headers={'Content-Type':'application/json'}, method='POST')
draft = json.loads(urllib.request.urlopen(req1).read())
article = draft['news_item'][0]

data = {
    'media_id': media_id,
    'index': 0,
    'articles': {
        'title': '我给自己造了个AI管家，它现在替我干活了',
        'author': article.get('author',''),
        'digest': article.get('digest',''),
        'content': article['content'],
        'thumb_media_id': article['thumb_media_id'],
        'content_source_url': article.get('content_source_url',''),
        'need_open_comment': 0
    }
}
body2 = json.dumps(data, ensure_ascii=False).encode('utf-8')
req2 = urllib.request.Request(f'https://api.weixin.qq.com/cgi-bin/draft/update?access_token={token}', data=body2, headers={'Content-Type':'application/json; charset=utf-8'}, method='POST')
result = json.loads(urllib.request.urlopen(req2).read())
print('result:', result)

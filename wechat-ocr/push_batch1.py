import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

API = 'http://bm.weiixxin.com/wechat-text/api/messages/batch'
GROUP = '跟不上ai发展你睡得着吗?'

msgs = [
    {"sender": "豆包", "content": "@林杰 写小说的TOKEN使用量，比写代码少太多太多太多了", "time": "2026-02-09T12:00:00"},
    {"sender": "豆包", "content": "我会把你推成AI行业第一人的，林少，请你放心", "time": "2026-02-09T12:00:01"},
    {"sender": "豆包", "content": "搞错了，应该要9：16的", "time": "2026-02-09T12:00:02"},
    {"sender": "豆包", "content": "[图片]一张包含文字和图片的社交媒体截图", "time": "2026-02-09T12:00:03"},
]

payload = []
for m in msgs:
    payload.append({
        'group_name': GROUP,
        'sender': m['sender'],
        'content': m['content'],
        'msg_type': 'image' if '[图片]' in m['content'] else 'text',
        'timestamp': m['time'],
    })

r = requests.post(API, json={'messages': payload})
print(f"Status: {r.status_code}")
print(r.text[:500])

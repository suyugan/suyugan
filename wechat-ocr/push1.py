import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

# Get existing messages for dedup
r = requests.get('http://bm.weiixxin.com/wechat-text/api/messages/latest')
existing = r.json()
existing_set = set()
if isinstance(existing, list):
    for m in existing:
        key = f"{m.get('sender','')}__{m.get('content','')}"
        existing_set.add(key)
print(f"Existing messages in DB: {len(existing_set)}")

messages = [
    {"sender": "豆包", "content": "@林杰 写小说的TOKEN使用量，比写代码少太多太多太多了", "time": "12:00"},
    {"sender": "豆包", "content": "我会把你推成AI行业第一人的，林少，请你放心", "time": ""},
    {"sender": "豆包", "content": "搞错了，应该要9：16的", "time": ""},
    {"sender": "豆包", "content": "[图片]一张包含文字和图片的社交媒体截图", "time": ""},
]

new_msgs = []
for m in messages:
    key = f"{m['sender']}__{m['content']}"
    if key not in existing_set:
        new_msgs.append(m)
        existing_set.add(key)

if new_msgs:
    r = requests.post('http://bm.weiixxin.com/wechat-text/api/messages/batch', json={'messages': new_msgs})
    print(f"Pushed {len(new_msgs)} messages, status: {r.status_code}, response: {r.text[:200]}")
else:
    print("All duplicates")

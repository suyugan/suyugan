import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

API = 'http://bm.weiixxin.com/wechat-text/api/messages/batch'
GROUP = '跟不上ai发展你睡得着吗?'

# Get existing for dedup
r = requests.get('http://bm.weiixxin.com/wechat-text/api/messages/latest')
existing = r.json().get('messages', [])
existing_set = set()
for m in existing:
    key = f"{m['sender']}__{m['content']}"
    existing_set.add(key)

def push(messages_raw):
    """Push list of {sender, content, time} dicts"""
    new_msgs = []
    for m in messages_raw:
        key = f"{m['sender']}__{m['content']}"
        if key not in existing_set:
            new_msgs.append({
                'group_name': GROUP,
                'sender': m['sender'],
                'content': m['content'],
                'msg_type': 'image' if '[图片]' in m['content'] else 'text',
                'timestamp': m.get('time', ''),
            })
            existing_set.add(key)
    if new_msgs:
        r = requests.post(API, json={'messages': new_msgs})
        print(f"OK: pushed {len(new_msgs)}, status {r.status_code}")
        if r.status_code != 200:
            print(r.text[:300])
        return len(new_msgs)
    print("skip: all dupes")
    return 0

if __name__ == '__main__':
    msgs = json.loads(sys.argv[1])
    push(msgs)

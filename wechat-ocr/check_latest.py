import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')
r = requests.get('http://bm.weiixxin.com/wechat-text/api/messages/latest')
data = r.json()
# Print just the key info
if 'messages' in data:
    for m in data['messages'][-3:]:
        print(f"[{m.get('time','')}] {m.get('sender','')}: {m.get('content','')[:50]}")
elif 'message' in data:
    m = data['message']
    print(f"Latest: [{m.get('time','')}] {m.get('sender','')}: {m.get('content','')[:80]}")
else:
    # Just dump keys and truncated values
    for k, v in data.items():
        print(f"{k}: {str(v)[:200]}")

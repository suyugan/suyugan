import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')
r = requests.get('http://bm.weiixxin.com/wechat-text/api/messages/latest')
data = r.json()
if isinstance(data, list):
    for m in data[-10:]:
        print(f"[{m.get('time','')}] {m.get('sender','')}: {m.get('content','')[:80]}")
elif isinstance(data, dict):
    msgs = data.get('messages', data.get('data', []))
    if isinstance(msgs, list):
        for m in msgs[-10:]:
            print(f"[{m.get('time','')}] {m.get('sender','')}: {m.get('content','')[:80]}")
    else:
        print(json.dumps(data, ensure_ascii=False)[:500])

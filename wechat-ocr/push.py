import requests, json, sys

def push(msgs):
    r = requests.post('http://bm.weiixxin.com/wechat-text/api/messages/batch', json={'messages': msgs})
    print(r.status_code, r.text[:100])

GROUP = '跟不上ai的发展你睡得着吗？'

if __name__ == '__main__':
    data_file = sys.argv[1]
    with open(data_file, 'r', encoding='utf-8') as f:
        msgs = json.load(f)
    push(msgs)

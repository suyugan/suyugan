import requests
r = requests.post('http://106.55.158.137/wechat/api/groups', json={'name': 'testcreate'})
print(r.status_code, r.text)

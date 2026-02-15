#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

script = r'''
import json, urllib.request

APPID="wx9a447fddc9ba6a59"
APPSECRET="REDACTED_WECHAT_SECRET"

req0 = urllib.request.urlopen("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (APPID, APPSECRET))
token = json.loads(req0.read())["access_token"]

body = json.dumps({"offset":0,"count":10,"no_content":1}).encode("utf-8")
req1 = urllib.request.Request("https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token=%s" % token, data=body, headers={"Content-Type":"application/json"}, method="POST")
data = json.loads(urllib.request.urlopen(req1).read())

for item in data.get("item",[]):
    mid = item["media_id"]
    title = item["content"]["news_item"][0]["title"]
    ut = item.get("update_time","")
    print(f"{ut} | {title[:50]} | {mid}")
'''

sftp = ssh.open_sftp()
with sftp.open('/tmp/list_drafts.py', 'w') as f:
    f.write(script)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('python3 /tmp/list_drafts.py')
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print('ERR:', err)
ssh.close()

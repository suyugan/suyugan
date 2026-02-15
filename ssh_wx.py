import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD', timeout=10)
cmd = "curl -s 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wx9a447fddc9ba6a59&secret=REDACTED_WECHAT_SECRET'"
stdin, stdout, stderr = ssh.exec_command(cmd)
result = stdout.read().decode()
print("Result:", result)
data = json.loads(result)

if "access_token" in data:
    token = data["access_token"]
    print(f"TOKEN={token}")
else:
    print(f"FAILED: {data}")

ssh.close()

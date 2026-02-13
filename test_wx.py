import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')
stdin, stdout, stderr = ssh.exec_command("curl -s 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wx9a447fddc9ba6a59&secret=REDACTED_WECHAT_SECRET'")
print(stdout.read().decode())
print(stderr.read().decode())
ssh.close()

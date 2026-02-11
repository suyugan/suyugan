import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')
stdin, stdout, stderr = ssh.exec_command('sed -n "360,390p" /home/ubuntu/wechat-sync/frontend/index.html')
print(stdout.read().decode())
ssh.close()

import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

with open(r'D:\wechat-plugin-dev\frontend\showcase.html', 'r', encoding='utf-8') as f:
    html = f.read()

stdin, stdout, stderr = ssh.exec_command('cat > /home/ubuntu/wechat-sync/frontend/showcase.html', bufsize=-1)
stdin.write(html.encode('utf-8'))
stdin.channel.shutdown_write()
print("Deployed", len(html), "bytes")
ssh.close()

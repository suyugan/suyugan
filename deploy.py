import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

# Check file size
_, out, _ = ssh.exec_command('wc -c /home/ubuntu/wechat-sync/frontend/showcase.html')
print('File size:', out.read().decode().strip())

# Restart pm2
_, out, err = ssh.exec_command('pm2 restart wechat-sync 2>&1 | cat')
print('PM2:', out.read().decode().strip()[:200])

# Check HTTP
_, out, _ = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/wechat-sync/showcase')
print('HTTP status:', out.read().decode().strip())

ssh.close()

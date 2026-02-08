import paramiko, sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD', timeout=10)

# Run rebuild in background and check later
cmd = 'cd /home/ubuntu/wechat-text-viewer && rm -rf node_modules && npm install 2>&1 > /tmp/npm-install.log && pm2 restart wechat-text 2>&1 >> /tmp/npm-install.log &'
print(f'> {cmd}')
ssh.exec_command(cmd)
print('Started background install, waiting 60s...')
time.sleep(60)

stdin, stdout, stderr = ssh.exec_command('cat /tmp/npm-install.log 2>&1', timeout=10)
print(stdout.read().decode('utf-8', errors='replace')[:1000])

print('\nChecking API...')
stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:3001/api/messages?limit=2 2>&1', timeout=10)
print(stdout.read().decode('utf-8', errors='replace')[:500])
ssh.close()

import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD', timeout=10)
cmds = [
    'pm2 list --no-color 2>/dev/null | head -20',
    'curl -s http://127.0.0.1:3002/api/stats',
    'curl -s "http://127.0.0.1:3002/api/messages?limit=2"',
    'wc -l /home/ubuntu/wechat-sync/db/messages.db 2>/dev/null || echo "no db"',
    'ls -la /home/ubuntu/wechat-sync/db/',
]
for cmd in cmds:
    print(f">>> {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode('utf-8', 'replace'))
    err = stderr.read().decode('utf-8', 'replace')
    if err: print(f"ERR: {err}")
    print("---")
ssh.close()

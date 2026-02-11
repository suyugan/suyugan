import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

# Check server config
cmds = [
    'ls /home/ubuntu/wechat-sync/frontend/',
    'head -50 /home/ubuntu/wechat-sync/server.js 2>/dev/null || head -50 /home/ubuntu/wechat-sync/index.js 2>/dev/null || head -50 /home/ubuntu/wechat-sync/app.js 2>/dev/null',
    'grep -rn "showcase\|frontend\|static\|express.static" /home/ubuntu/wechat-sync/*.js 2>/dev/null | head -20',
    'curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/wechat-sync/showcase.html',
    'curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/showcase',
    'pm2 show wechat-sync 2>&1 | grep -E "script|cwd" | head -5',
]
for c in cmds:
    _, out, err = ssh.exec_command(c)
    r = out.read().decode().strip()
    print(f'>>> {c[:60]}')
    print(r[:500] if r else err.read().decode().strip()[:200])
    print()
ssh.close()

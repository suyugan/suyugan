import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD', timeout=10)

def run(cmd, timeout=300):
    print(f'>> {cmd}', flush=True)
    _, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out, flush=True)
    if err: print(f'ERR: {err}', flush=True)
    return out

# Check node version
run('node -v')

# Try npm install with longer timeout - better-sqlite3 needs to compile
run('cd /home/ubuntu/wechat-sync && npm install better-sqlite3 2>&1')

# Restart and test
run('pm2 restart wechat-sync')
time.sleep(3)
run('pm2 logs wechat-sync --lines 5 --nostream')
run('curl -s http://127.0.0.1:3002/api/stats')

# Fix nginx - add wechat-sync to default
nginx = run('cat /etc/nginx/sites-enabled/default')
if 'wechat-sync' not in nginx:
    run("""sudo sed -i '/^}/i\\    location /wechat-sync/ {\\n        proxy_pass http://127.0.0.1:3002/;\\n        proxy_set_header Host $host;\\n        proxy_set_header X-Real-IP $remote_addr;\\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\\n        proxy_set_header X-Forwarded-Proto $scheme;\\n    }' /etc/nginx/sites-enabled/default""")
    run('sudo nginx -t 2>&1')
    run('sudo systemctl reload nginx')

# Test
run("""curl -s -X POST http://127.0.0.1:3002/api/messages -H "Content-Type: application/json" -d '{"msg_svr_id":"test001","from_user":"test@chatroom","real_sender":"wxid_test","sender_nick":"测试用户","content":"这是一条测试消息","msg_type":1,"create_time":1739174400}'""")
run('curl -s http://127.0.0.1:3002/api/messages?limit=3')
run('curl -s -o /dev/null -w "%{http_code}" http://bm.weiixxin.com/wechat-sync/')

ssh.close()
print('DONE', flush=True)
